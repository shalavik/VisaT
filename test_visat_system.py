#!/usr/bin/env python3
"""
VisaT System Integration Test
Comprehensive test of all system components
"""

import json
import requests
import time
from datetime import datetime

def test_visat_system():
    """Test the complete VisaT system"""
    
    print("🚀 VISAT SYSTEM INTEGRATION TEST")
    print("=" * 50)
    
    # Test data
    test_cases = [
        {
            "name": "Qualified Prospect - UK National",
            "data": {
                "full_name": "John Smith",
                "email": "john.smith@example.com",
                "nationality": "British",
                "current_location": "London",
                "financial_status": True,
                "current_visa_type": "",
                "how_heard": "Google Search",
                "additional_questions": "Looking for retirement visa options"
            },
            "expected_qualified": True
        },
        {
            "name": "Rejected - Blocked Nationality",
            "data": {
                "full_name": "Ahmed Hassan",
                "email": "ahmed.hassan@example.com",
                "nationality": "Myanmar",
                "current_location": "Yangon",
                "financial_status": True,
                "current_visa_type": "",
                "how_heard": "Facebook",
                "additional_questions": "Need visa consultation"
            },
            "expected_qualified": False
        },
        {
            "name": "Rejected - Insufficient Funds",
            "data": {
                "full_name": "Maria Garcia",
                "email": "maria.garcia@example.com",
                "nationality": "Spanish",
                "current_location": "Madrid",
                "financial_status": False,
                "current_visa_type": "",
                "how_heard": "WhatsApp",
                "additional_questions": "Student visa inquiry"
            },
            "expected_qualified": False
        }
    ]
    
    # Test results
    results = {
        "health_check": False,
        "qualification_engine": [],
        "form_processing": [],
        "whatsapp_webhook": False,
        "facebook_webhook": False,
        "email_test": False,
        "stats_endpoint": False
    }
    
    base_url = "http://localhost:5000"
    
    print("\n1. Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['service']}")
            results["health_check"] = True
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print("\n2. Testing Qualification Engine...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test Case {i}: {test_case['name']}")
        try:
            response = requests.post(
                f"{base_url}/api/qualify",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                qualified = result.get("qualified", False)
                expected = test_case["expected_qualified"]
                
                if qualified == expected:
                    print(f"   ✅ Qualification correct: {qualified}")
                    results["qualification_engine"].append(True)
                else:
                    print(f"   ❌ Qualification incorrect: got {qualified}, expected {expected}")
                    results["qualification_engine"].append(False)
                
                print(f"   📋 Reason: {result.get('reason', 'N/A')}")
                print(f"   💬 Message: {result.get('message', 'N/A')[:50]}...")
                
            else:
                print(f"   ❌ API error: {response.status_code}")
                results["qualification_engine"].append(False)
                
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            results["qualification_engine"].append(False)
    
    print("\n3. Testing Form Processing...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Form Test {i}: {test_case['name']}")
        try:
            # Simulate Google Forms webhook data
            form_webhook_data = {
                "responses": test_case["data"]
            }
            
            response = requests.post(
                f"{base_url}/webhook/forms",
                json=form_webhook_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Form processing successful")
                print(f"   📊 Status: {result.get('status', 'unknown')}")
                results["form_processing"].append(True)
            else:
                print(f"   ❌ Form processing failed: {response.status_code}")
                results["form_processing"].append(False)
                
        except Exception as e:
            print(f"   ❌ Form test error: {e}")
            results["form_processing"].append(False)
    
    print("\n4. Testing WhatsApp Webhook...")
    try:
        # Simulate WhatsApp webhook data
        whatsapp_data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "id": "wamid.test123",
                            "text": {"body": "Hello, I need visa help"},
                            "type": "text",
                            "timestamp": str(int(time.time()))
                        }]
                    }
                }]
            }]
        }
        
        response = requests.post(
            f"{base_url}/webhook/whatsapp",
            json=whatsapp_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ WhatsApp webhook processed: {result.get('status')}")
            results["whatsapp_webhook"] = True
        else:
            print(f"❌ WhatsApp webhook failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ WhatsApp webhook error: {e}")
    
    print("\n5. Testing Facebook Webhook...")
    try:
        # Simulate Facebook webhook data
        facebook_data = {
            "entry": [{
                "messaging": [{
                    "sender": {"id": "facebook_user_123"},
                    "recipient": {"id": "page_id_456"},
                    "message": {"text": "Hi, interested in Thailand visa"},
                    "timestamp": int(time.time() * 1000)
                }]
            }]
        }
        
        response = requests.post(
            f"{base_url}/webhook/facebook",
            json=facebook_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Facebook webhook processed: {result.get('status')}")
            results["facebook_webhook"] = True
        else:
            print(f"❌ Facebook webhook failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Facebook webhook error: {e}")
    
    print("\n6. Testing Email Functionality...")
    try:
        email_test_data = {
            "email": "test@example.com",
            "subject": "VisaT System Test",
            "message": "This is a test email from the VisaT system."
        }
        
        response = requests.post(
            f"{base_url}/api/test-email",
            json=email_test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email test successful: {result.get('status')}")
            results["email_test"] = True
        else:
            print(f"❌ Email test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Email test error: {e}")
    
    print("\n7. Testing Statistics Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics endpoint working")
            print(f"   📊 Total leads: {stats.get('total_leads', 0)}")
            print(f"   ✅ Qualified: {stats.get('qualified_leads', 0)}")
            results["stats_endpoint"] = True
        else:
            print(f"❌ Statistics failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Statistics error: {e}")
    
    # Print final results
    print("\n" + "=" * 50)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    # Health check
    total_tests += 1
    if results["health_check"]:
        passed_tests += 1
        print("✅ Health Check: PASSED")
    else:
        print("❌ Health Check: FAILED")
    
    # Qualification engine
    qualification_passed = sum(results["qualification_engine"])
    qualification_total = len(results["qualification_engine"])
    total_tests += qualification_total
    passed_tests += qualification_passed
    print(f"{'✅' if qualification_passed == qualification_total else '❌'} Qualification Engine: {qualification_passed}/{qualification_total}")
    
    # Form processing
    form_passed = sum(results["form_processing"])
    form_total = len(results["form_processing"])
    total_tests += form_total
    passed_tests += form_passed
    print(f"{'✅' if form_passed == form_total else '❌'} Form Processing: {form_passed}/{form_total}")
    
    # Webhooks and endpoints
    webhook_tests = [
        ("WhatsApp Webhook", results["whatsapp_webhook"]),
        ("Facebook Webhook", results["facebook_webhook"]),
        ("Email Test", results["email_test"]),
        ("Statistics", results["stats_endpoint"])
    ]
    
    for test_name, passed in webhook_tests:
        total_tests += 1
        if passed:
            passed_tests += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Overall result
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print("\n" + "=" * 50)
    print(f"🏆 OVERALL RESULT: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 SYSTEM STATUS: READY FOR DEPLOYMENT")
        return True
    elif success_rate >= 60:
        print("⚠️  SYSTEM STATUS: NEEDS MINOR FIXES")
        return False
    else:
        print("🚨 SYSTEM STATUS: NEEDS MAJOR FIXES")
        return False

if __name__ == "__main__":
    print("Starting VisaT System Test...")
    print("Make sure the Flask app is running on localhost:5000")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
        success = test_visat_system()
        
        if success:
            print("\n✅ VisaT system is ready for production!")
        else:
            print("\n⚠️  VisaT system needs attention before deployment.")
            
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user.")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}") 