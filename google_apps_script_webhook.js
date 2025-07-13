/**
 * Google Apps Script for Google Forms Webhook Integration
 * 
 * SETUP INSTRUCTIONS:
 * 1. Open your Google Form
 * 2. Click "Extensions" > "Apps Script"
 * 3. Replace the default code with this script
 * 4. Update the WEBHOOK_URL to your server URL
 * 5. Save and authorize the script
 * 6. The script will automatically run when someone submits the form
 */

// ⚠️ IMPORTANT: Update this URL to your server's webhook endpoint
const WEBHOOK_URL = 'http://localhost:5002/webhook/forms'; // For local testing
// For production, use your public URL: const WEBHOOK_URL = 'https://your-domain.com/webhook/forms';

/**
 * This function automatically runs when a form is submitted
 * You don't need to call this manually - it's triggered by form submissions
 */
function onFormSubmit(e) {
  try {
    console.log('Form submission triggered');
    
    // Get the form response
    const form = FormApp.getActiveForm();
    const formResponse = e.response;
    const itemResponses = formResponse.getItemResponses();
    
    // Build the data object with question text as keys
    const formData = {};
    
    itemResponses.forEach(function(itemResponse) {
      const question = itemResponse.getItem().getTitle();
      const answer = itemResponse.getResponse();
      formData[question] = answer;
      console.log('Question: ' + question + ', Answer: ' + answer);
    });
    
    // Add metadata
    formData['timestamp'] = new Date().toISOString();
    formData['form_title'] = form.getTitle();
    formData['response_id'] = formResponse.getId();
    
    console.log('Sending data to webhook:', JSON.stringify(formData, null, 2));
    
    // Send to webhook
    const response = UrlFetchApp.fetch(WEBHOOK_URL, {
      'method': 'POST',
      'headers': {
        'Content-Type': 'application/json',
      },
      'payload': JSON.stringify(formData)
    });
    
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    console.log('Webhook response code:', responseCode);
    console.log('Webhook response:', responseText);
    
    if (responseCode === 200) {
      console.log('✅ Successfully sent form data to webhook');
    } else {
      console.error('❌ Webhook request failed with code:', responseCode);
    }
    
  } catch (error) {
    console.error('❌ Error in onFormSubmit:', error.toString());
    
    // Optional: Send error notification email to admin
    // GmailApp.sendEmail('your-email@gmail.com', 'Form Webhook Error', error.toString());
  }
}

/**
 * Setup function to install the trigger
 * Run this once to set up the automatic form submission trigger
 */
function setupTrigger() {
  try {
    // Delete existing triggers to avoid duplicates
    const triggers = FormApp.getActiveForm().getTriggers();
    triggers.forEach(trigger => FormApp.deleteTrigger(trigger));
    
    // Create new trigger for form submissions
    FormApp.getActiveForm().onFormSubmit(onFormSubmit);
    
    console.log('✅ Form submission trigger installed successfully');
    console.log('Webhook URL configured:', WEBHOOK_URL);
    
  } catch (error) {
    console.error('❌ Error setting up trigger:', error.toString());
  }
}

/**
 * Test function to verify webhook connectivity
 * Run this manually to test the webhook connection
 */
function testWebhookConnection() {
  try {
    const testData = {
      'Full Name': 'Test User',
      'Email Address': 'test@example.com',
      'Nationality': 'Spain',
      'Current Country': 'Thailand',
      'Do you have more than 500k BTH in your bank account?': 'Yes',
      'WhatsApp Number (with country code)': '+34666123456',
      'timestamp': new Date().toISOString(),
      'test_mode': true
    };
    
    console.log('Testing webhook with data:', JSON.stringify(testData, null, 2));
    
    const response = UrlFetchApp.fetch(WEBHOOK_URL, {
      'method': 'POST',
      'headers': {
        'Content-Type': 'application/json',
      },
      'payload': JSON.stringify(testData)
    });
    
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    console.log('Test webhook response code:', responseCode);
    console.log('Test webhook response:', responseText);
    
    if (responseCode === 200) {
      console.log('✅ Webhook test successful!');
      return true;
    } else {
      console.error('❌ Webhook test failed with code:', responseCode);
      return false;
    }
    
  } catch (error) {
    console.error('❌ Error testing webhook:', error.toString());
    return false;
  }
}

/**
 * Get form field mapping for debugging
 * Run this to see what your form fields are called
 */
function getFormFields() {
  try {
    const form = FormApp.getActiveForm();
    const items = form.getItems();
    
    console.log('=== FORM FIELDS ===');
    console.log('Form Title:', form.getTitle());
    console.log('Number of fields:', items.length);
    
    items.forEach(function(item, index) {
      console.log(`Field ${index + 1}: "${item.getTitle()}" (Type: ${item.getType()})`);
    });
    
    console.log('=== END FORM FIELDS ===');
    
  } catch (error) {
    console.error('❌ Error getting form fields:', error.toString());
  }
} 