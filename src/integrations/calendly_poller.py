import logging
import threading
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .calendly_client import CalendlyClient
from .booking_sheet_handler import BookingSheetHandler

logger = logging.getLogger(__name__)

class CalendlyPoller:
    def __init__(self):
        self.calendly_client = CalendlyClient()
        self.booking_handler = BookingSheetHandler()
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self._lock = threading.Lock()
        
        logger.info("🔄 CalendlyPoller initialized")
    
    def start_polling(self):
        """Start the polling scheduler"""
        with self._lock:
            if self.is_running:
                logger.warning("Polling is already running")
                return
            
            try:
                # Schedule polling every 5 minutes
                self.scheduler.add_job(
                    func=self.poll_and_update,
                    trigger=IntervalTrigger(minutes=5),
                    id='calendly_polling',
                    name='Calendly Booking Poller',
                    replace_existing=True
                )
                
                self.scheduler.start()
                self.is_running = True
                
                # Run initial poll
                self.poll_and_update()
                
                logger.info("✅ Started Calendly polling (every 5 minutes)")
                
            except Exception as e:
                logger.error(f"Failed to start polling: {e}")
                raise
    
    def stop_polling(self):
        """Stop the polling scheduler"""
        with self._lock:
            if not self.is_running:
                logger.warning("Polling is not running")
                return
            
            try:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("⏹️  Stopped Calendly polling")
                
            except Exception as e:
                logger.error(f"Failed to stop polling: {e}")
    
    def poll_and_update(self):
        """Poll Calendly for new/updated bookings and update Google Sheet"""
        try:
            logger.info("🔍 Polling Calendly for booking updates...")
            
            # Get the timestamp of the last known booking to optimize polling
            last_booking_time = self.booking_handler.get_latest_booking_timestamp()
            
            if last_booking_time:
                # Poll from last known booking time minus 1 hour buffer
                min_start_time = last_booking_time - timedelta(hours=1)
            else:
                # First time polling - get bookings from last 7 days
                min_start_time = datetime.utcnow() - timedelta(days=7)
            
            # Get scheduled events
            scheduled_events = self.calendly_client.get_scheduled_events(
                min_start_time=min_start_time
            )
            
            # Get canceled events  
            canceled_events = self.calendly_client.get_canceled_events(
                min_start_time=min_start_time
            )
            
            # Process all events
            all_events = scheduled_events + canceled_events
            
            if not all_events:
                logger.info("📅 No new booking updates found")
                return
            
            # Update Google Sheet with each booking
            updated_count = 0
            for event in all_events:
                if self._process_event(event):
                    updated_count += 1
            
            logger.info(f"✅ Processed {updated_count} booking updates")
            
        except Exception as e:
            logger.error(f"Error during polling: {e}")
    
    def _process_event(self, event):
        """Process a single event and update the sheet"""
        try:
            # Process each invitee in the event
            invitees = event.get('invitees', [])
            if not invitees:
                logger.warning(f"No invitees found for event {event.get('event_uuid')}")
                return False
            
            success_count = 0
            for invitee in invitees:
                booking_data = {
                    'event_uuid': event.get('event_uuid'),
                    'invitee_email': invitee.get('email'),
                    'invitee_name': invitee.get('name'),
                    'scheduled_time': event.get('start_time'),
                    'end_time': event.get('end_time'),
                    'status': event.get('status', 'active'),
                    'created_at': event.get('created_at'),
                    'updated_at': event.get('updated_at'),
                    'event_type': event.get('event_type')
                }
                
                if self.booking_handler.upsert_booking(booking_data):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error processing event {event.get('event_uuid', 'unknown')}: {e}")
            return False
    
    def manual_poll(self):
        """Manually trigger a poll - useful for testing"""
        logger.info("🔄 Manual polling triggered")
        self.poll_and_update()
        return {"status": "completed", "message": "Manual poll completed"}
    
    def get_status(self):
        """Get current polling status"""
        return {
            "is_running": self.is_running,
            "scheduler_running": self.scheduler.running if hasattr(self.scheduler, 'running') else False,
            "next_run_time": str(self.scheduler.get_job('calendly_polling').next_run_time) if self.is_running else None,
            "booking_stats": self.booking_handler.get_booking_stats()
        } 