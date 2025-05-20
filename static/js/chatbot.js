
$(document).ready(function() {
    // Chat Bot Logic
    const chatMessages = $('#chat-messages');
    const chatInput = $('#chat-input');
    const sendButton = $('#send-message');
    
    // Quick response buttons
    $('.quick-response-btn').click(function() {
        const response = $(this).data('response');
        chatInput.val(response);
        sendMessage();
    });
    
    // Send message when Send button is clicked
    sendButton.click(function() {
        sendMessage();
    });
    
    // Send message when Enter key is pressed
    chatInput.keypress(function(e) {
        if (e.which === 13) {
            sendMessage();
        }
    });
    

    
    // Live chat functionality
    $('#send-live-message').click(function() {
        const message = $('#live-chat-input').val().trim();
        if (message) {
            // Add user message
            $('#live-chat-messages').append(`
                <div class="chat-message user-message mb-3 text-end">
                    <div class="message-content p-3 rounded">
                        <p class="mb-0">${message}</p>
                    </div>
                    <small class="text-muted">Just now</small>
                </div>
            `);
            
            // Clear input
            $('#live-chat-input').val('');
            
            // Scroll to bottom
            scrollToBottom($('#live-chat-messages'));
            
            // Simulate typing
            setTimeout(function() {
                $('#live-chat-messages').append(`
                    <div class="chat-message bot-message mb-3">
                        <div class="message-content p-3 rounded">
                            <p class="mb-0"><strong>Priya:</strong> I understand your concern about "${message}". Let me check this for you right away.</p>
                        </div>
                        <small class="text-muted">Just now</small>
                    </div>
                `);
                
                // Scroll to bottom
                scrollToBottom($('#live-chat-messages'));
            }, 1500);
        }
    });
    
    // Live chat input enter key
    $('#live-chat-input').keypress(function(e) {
        if (e.which === 13) {
            $('#send-live-message').click();
        }
    });
    
    // Function to send message
    function sendMessage() {
        const message = chatInput.val().trim();
        
        if (message) {
            // Add user message to chat
            chatMessages.append(`
                <div class="chat-message user-message mb-3 text-end">
                    <div class="message-content p-3 rounded">
                        <p class="mb-0">${message}</p>
                    </div>
                    <small class="text-muted">Just now</small>
                </div>
            `);
            
            // Clear input
            chatInput.val('');
            
            // Scroll to bottom
            scrollToBottom(chatMessages);
            
            // Process the message and get response
            const response = getBotResponse(message.toLowerCase());
            
            // Simulate typing delay
            setTimeout(function() {
                // Add bot response
                chatMessages.append(`
                    <div class="chat-message bot-message mb-3">
                        <div class="message-content p-3 rounded">
                            <p class="mb-0">${response}</p>
                        </div>
                        <small class="text-muted">Just now</small>
                    </div>
                `);
                
                // Scroll to bottom
                scrollToBottom(chatMessages);
            }, 1000);
        }
    }
    
    // Function to get bot response based on user message
    function getBotResponse(message) {
        // Check for keywords in the message and return appropriate response
        if (message.includes('hello') || message.includes('hi') || message.includes('hey')) {
            return "Hello! How can I help you today?";
        } else if (message.includes('track') && message.includes('order')) {
            return "To track your order, please login to your account and go to 'My Orders' section. You can view the status of all your orders there. If you have any specific order number, you can also share it with me.";
        } else if (message.includes('return') || message.includes('policy')) {
            return "We offer a 7-day return policy for all products in their original condition with tags attached. Custom-designed products cannot be returned unless there is a manufacturing defect. For more details, please visit our Returns page.";
        } else if (message.includes('delivery') || message.includes('shipping time')) {
            return "Standard delivery takes 3-5 business days within major cities and 5-7 business days for other locations. Express delivery (available at additional cost) takes 1-2 business days.";
        } else if (message.includes('international') && message.includes('shipping')) {
            return "Yes, we ship internationally to select countries. International shipping typically takes 7-14 business days depending on the destination country and customs processing.";
        } else if (message.includes('custom') && message.includes('design')) {
            return "Our custom design process involves four steps: selecting your design type, providing measurements, choosing fabric and design details, and final review. Custom designs typically take 2-3 weeks for production. Would you like to start a custom design?";
        } else if (message.includes('payment') && message.includes('option')) {
            return "We accept various payment methods including credit/debit cards, UPI, net banking, and cash on delivery (for orders under ₹10,000).";
        } else if (message.includes('size') && message.includes('chart')) {
            return "You can find our size chart on each product page. We also offer custom sizing for most of our products. Would you like guidance on taking measurements?";
        } else if (message.includes('cancel') && message.includes('order')) {
            return "You can cancel your order within 24 hours of placing it if it hasn't been shipped yet. To cancel, go to 'My Orders' in your account and select the cancel option for the specific order.";
        } else if (message.includes('contact') || message.includes('support team')) {
            return "You can reach our support team via email at support@bhaviindia.com or call us at +91 1234567890 during business hours (Mon-Sat, 10AM-7PM).";
        } else if (message.includes('bulk') && message.includes('order')) {
            return "For bulk orders, please visit our Bulk Orders page and fill out the inquiry form. Our team will contact you with custom pricing and options based on your requirements.";
        } else if (message.includes('tailor') || message.includes('job') || message.includes('employment')) {
            return "We're always looking for skilled tailors! Visit our Tailor Jobs page to see current opportunities and apply. We offer both in-workshop positions and work-from-home arrangements.";
        } else if (message.includes('fabric') || message.includes('material')) {
            return "We use a variety of premium fabrics including cotton, silk, georgette, crepe, and more. The specific fabric details are mentioned on each product page along with care instructions.";
        } else if (message.includes('thank')) {
            return "You're welcome! Is there anything else I can help you with?";
        } else if (message.includes('bye') || message.includes('goodbye')) {
            return "Thank you for chatting with us! Feel free to come back if you have more questions. Have a great day!";
        } else {
            return "I'm not sure I understand your query. Could you please rephrase or select one of the quick options below? Alternatively, you can connect with a live agent for more personalized assistance.";
        }
    }
    
    // Function to scroll to bottom of chat container
    function scrollToBottom(container) {
        container.scrollTop(container[0].scrollHeight);
    }
    
    // Add CSS for chat bubbles
    $("<style>")
        .prop("type", "text/css")
        .html(`
            .chat-message {
                max-width: 85%;
                margin-bottom: 1rem;
            }
            
            .bot-message {
                align-self: flex-start;
            }
            
            .bot-message .message-content {
                background-color: #f0f2f5;
                color: #333;
            }
            
            .user-message {
                align-self: flex-end;
                margin-left: auto;
            }
            
            .user-message .message-content {
                background-color: #6b4226;
                color: white;
            }
            
            .system-message .message-content {
                background-color: #e8f1ff;
                color: #333;
                font-size: 0.85rem;
            }
            
            #chat-messages, #live-chat-messages {
                display: flex;
                flex-direction: column;
            }
        `)
        .appendTo("head");
});
