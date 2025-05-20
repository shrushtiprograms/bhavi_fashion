/**
 * Bhavi India Fashion - Chatbot Functionality
 * 
 * This file handles the simple FAQ chatbot interaction for customer support.
 */

document.addEventListener('DOMContentLoaded', function() {
    initChatbot();
});

function initChatbot() {
    const chatbotButton = document.querySelector('.chatbot-button');
    const chatbotWindow = document.querySelector('.chatbot-window');
    const chatbotClose = document.querySelector('.chatbot-close');
    const chatMessages = document.querySelector('.chatbot-messages');
    const chatForm = document.querySelector('.chatbot-form');
    const chatInput = document.querySelector('.chatbot-input input');
    
    if (!chatbotButton || !chatbotWindow) return;
    
    // Toggle chatbot visibility
    chatbotButton.addEventListener('click', function() {
        chatbotWindow.style.display = 'flex';
        chatbotButton.style.display = 'none';
        
        // Add welcome message if there are no messages yet
        if (chatMessages.children.length === 0) {
            addBotMessage("👋 Hello! Welcome to Bhavi India Fashion. How can I help you today?", 500);
            
            setTimeout(() => {
                addBotMessage("You can ask me about our products, shipping, returns, or custom designs!", 1000);
                
                // Add suggested questions
                setTimeout(() => {
                    addSuggestedQuestions([
                        "What products do you offer?", 
                        "How long does shipping take?", 
                        "How to return a product?",
                        "Do you have custom design options?"
                    ]);
                }, 1500);
            }, 1000);
        }
        
        // Focus on input
        setTimeout(() => {
            chatInput.focus();
        }, 300);
    });
    
    // Close chatbot
    chatbotClose.addEventListener('click', function() {
        chatbotWindow.style.display = 'none';
        chatbotButton.style.display = 'flex';
    });
    
    // Handle form submission
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            
            if (message) {
                // Add user message
                addUserMessage(message);
                
                // Clear input
                chatInput.value = '';
                
                // Get bot response
                const response = getBotResponse(message);
                
                // Add bot message with typing delay
                setTimeout(() => {
                    addBotMessage(response.message);
                    
                    // If there are suggested follow-up questions
                    if (response.suggestions && response.suggestions.length > 0) {
                        setTimeout(() => {
                            addSuggestedQuestions(response.suggestions);
                        }, 500);
                    }
                }, 500);
            }
        });
    }
    
    // Add user message to chat
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message user-message';
        messageElement.innerHTML = `<div class="message-content">${message}</div>`;
        
        chatMessages.appendChild(messageElement);
        scrollToBottom();
    }
    
    // Add bot message to chat
    function addBotMessage(message, delay = 0) {
        setTimeout(() => {
            const messageElement = document.createElement('div');
            messageElement.className = 'chat-message bot-message';
            messageElement.innerHTML = `<div class="message-content">${message}</div>`;
            
            chatMessages.appendChild(messageElement);
            scrollToBottom();
        }, delay);
    }
    
    // Add suggested questions as clickable buttons
    function addSuggestedQuestions(questions) {
        const suggestionsElement = document.createElement('div');
        suggestionsElement.className = 'suggested-questions';
        
        let html = '<div class="message-content"><div class="suggestions">';
        questions.forEach(question => {
            html += `<button class="suggestion-btn">${question}</button>`;
        });
        html += '</div></div>';
        
        suggestionsElement.innerHTML = html;
        chatMessages.appendChild(suggestionsElement);
        scrollToBottom();
        
        // Add click handlers to suggestions
        suggestionsElement.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const question = this.textContent;
                addUserMessage(question);
                
                // Get bot response
                const response = getBotResponse(question);
                
                // Add bot message with typing delay
                setTimeout(() => {
                    addBotMessage(response.message);
                    
                    // If there are suggested follow-up questions
                    if (response.suggestions && response.suggestions.length > 0) {
                        setTimeout(() => {
                            addSuggestedQuestions(response.suggestions);
                        }, 500);
                    }
                }, 500);
            });
        });
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Get bot response based on user input
    function getBotResponse(message) {
        // Convert to lowercase for easier matching
        const input = message.toLowerCase();
        
        // Define responses
        const responses = [
            {
                keywords: ['hello', 'hi', 'hey', 'greeting'],
                response: "👋 Hello! How can I help you today?",
                suggestions: [
                    "What products do you offer?", 
                    "How long does shipping take?", 
                    "Do you have custom design options?"
                ]
            },
            {
                keywords: ['product', 'products', 'offer', 'sell', 'collection'],
                response: "We offer a wide range of traditional Indian fashion including Kurtis, Cholis, Dupattas, Blouses, and Kurti Pant Sets. Our products are made with high-quality fabrics and traditional designs. Would you like to see our collection?",
                suggestions: [
                    "Show me Kurtis", 
                    "Show me Blouses", 
                    "Tell me about custom designs",
                    "What are your bestsellers?"
                ]
            },
            {
                keywords: ['kurti', 'kurtis'],
                response: "Our Kurti collection features traditional designs with modern touches. We have casual, formal, and festive kurtis in various sizes and colors. You can browse our collection <a href='/products/category/kurti/'>here</a>.",
                suggestions: [
                    "What sizes do you offer?",
                    "How to find my size?",
                    "Show me other products"
                ]
            },
            {
                keywords: ['choli', 'cholis'],
                response: "Our Choli collection includes traditional and contemporary designs perfect for festivals and ceremonies. View our collection <a href='/products/category/choli/'>here</a>.",
                suggestions: [
                    "What sizes do you offer?",
                    "Can I get a custom choli?"
                ]
            },
            {
                keywords: ['dupatta', 'dupattas'],
                response: "We have beautiful Dupattas in various fabrics, colors, and embroidery styles. Check them out <a href='/products/category/dupatta/'>here</a>.",
                suggestions: [
                    "What fabrics do you use?",
                    "Do you offer matching sets?"
                ]
            },
            {
                keywords: ['blouse', 'blouses'],
                response: "Our Blouse collection features designs for every occasion. Browse our collection <a href='/products/category/blouse/'>here</a>.",
                suggestions: [
                    "What sizes do you offer?",
                    "Can I get a custom blouse?"
                ]
            },
            {
                keywords: ['size', 'sizes', 'size chart', 'measurement'],
                response: "We offer sizes from XS to 3XL. You can find detailed size charts on each product page. For a perfect fit, you can also use our custom design option where you can provide your exact measurements.",
                suggestions: [
                    "Tell me about custom designs",
                    "How do I measure myself?",
                    "What if my size is not available?"
                ]
            },
            {
                keywords: ['measure', 'measurements', 'measuring'],
                response: "For accurate measurements, use a soft measuring tape. Measure your bust at the fullest part, waist at the narrowest part, and hips at the widest part. For detailed instructions, check our size guide on each product page or visit our <a href='/custom-designs/'>custom design</a> section.",
                suggestions: [
                    "Tell me about custom designs",
                    "What if my size doesn't match the chart?"
                ]
            },
            {
                keywords: ['custom', 'customize', 'custom design', 'custom designs'],
                response: "Yes! We offer custom design options where you can choose your fabric, color, and provide your measurements for a perfect fit. You can start your custom design order <a href='/custom-designs/'>here</a>.",
                suggestions: [
                    "How long does custom design take?",
                    "What information do I need to provide?",
                    "How much does it cost?"
                ]
            },
            {
                keywords: ['shipping', 'delivery', 'ship', 'deliver'],
                response: "We ship across India and delivery usually takes 3-5 business days for metro cities and 5-7 days for other areas. You can check delivery availability and estimated time by entering your PIN code on the product page.",
                suggestions: [
                    "Is there free shipping?",
                    "Can I track my order?",
                    "Do you ship internationally?"
                ]
            },
            {
                keywords: ['free shipping', 'shipping cost'],
                response: "We offer free shipping on orders above ₹500. For orders below ₹500, a shipping charge of ₹50 is applied.",
                suggestions: [
                    "What are your bestsellers?",
                    "How long does shipping take?",
                    "Can I track my order?"
                ]
            },
            {
                keywords: ['track', 'tracking', 'order status'],
                response: "Yes, you can track your order from your account. After placing your order, you'll receive a confirmation email with tracking information. You can also check your order status from the 'My Orders' section in your profile.",
                suggestions: [
                    "What if my order is delayed?",
                    "How to contact customer support?"
                ]
            },
            {
                keywords: ['international', 'abroad', 'overseas'],
                response: "Currently, we only ship within India. We're working on expanding our shipping options and hope to offer international shipping soon!",
                suggestions: [
                    "What are your bestsellers?",
                    "Tell me about custom designs"
                ]
            },
            {
                keywords: ['return', 'returns', 'exchange'],
                response: "We accept returns within 7 days of delivery if the product is unused and in its original packaging. For returns or exchanges, please contact our customer support team through the 'Contact Us' page or email us at returns@bhaviindiafashion.com.",
                suggestions: [
                    "How to initiate a return?",
                    "What's your refund policy?",
                    "Contact customer support"
                ]
            },
            {
                keywords: ['refund', 'money back'],
                response: "Refunds are processed within 7-10 business days after we receive the returned product. The amount will be credited back to your original payment method.",
                suggestions: [
                    "How to initiate a return?",
                    "Contact customer support"
                ]
            },
            {
                keywords: ['payment', 'pay', 'payment methods'],
                response: "We accept various payment methods including Credit/Debit Cards, Net Banking, UPI (Google Pay, PhonePe, BHIM), and Cash on Delivery (available in select areas).",
                suggestions: [
                    "Is COD available in my area?",
                    "Is online payment secure?"
                ]
            },
            {
                keywords: ['cod', 'cash on delivery'],
                response: "Cash on Delivery (COD) is available in select areas. You can check COD availability by entering your PIN code during checkout.",
                suggestions: [
                    "What other payment methods do you accept?",
                    "How long does shipping take?"
                ]
            },
            {
                keywords: ['bestseller', 'bestsellers', 'popular', 'trending'],
                response: "Our bestsellers include our Embroidered Kurtis, Designer Blouses, and Festive Cholis. You can view our popular products <a href='/products/?sort_by=popularity'>here</a>.",
                suggestions: [
                    "Show me new arrivals",
                    "What's on sale?"
                ]
            },
            {
                keywords: ['discount', 'sale', 'offer'],
                response: "We regularly have seasonal sales and offers. Check our website for ongoing discounts or sign up for our newsletter to be notified about upcoming sales.",
                suggestions: [
                    "Show me current offers",
                    "How to sign up for newsletter?"
                ]
            },
            {
                keywords: ['fabric', 'material', 'cotton', 'silk'],
                response: "We use high-quality fabrics including Cotton, Silk, Georgette, Chiffon, and Crepe. Each product page lists the specific fabric used for that item.",
                suggestions: [
                    "Do you have cotton kurtis?",
                    "Do you have silk blouses?"
                ]
            },
            {
                keywords: ['bulk', 'wholesale', 'bulk order'],
                response: "Yes, we offer bulk ordering options for retailers and wholesalers. You can submit a bulk order inquiry <a href='/bulk-orders/'>here</a>.",
                suggestions: [
                    "What's the minimum quantity for bulk orders?",
                    "Do you offer discounts on bulk orders?"
                ]
            },
            {
                keywords: ['tailor', 'job', 'work', 'career', 'employment'],
                response: "We're always looking for talented tailors to join our team. If you're interested, you can submit your application <a href='/tailor-jobs/'>here</a>.",
                suggestions: [
                    "What skills are required?",
                    "Is work from home available?"
                ]
            },
            {
                keywords: ['contact', 'help', 'support', 'customer service'],
                response: "You can contact our customer support team through email at support@bhaviindiafashion.com or call us at +91-1234567890 between 9 AM and 6 PM (Monday to Saturday).",
                suggestions: [
                    "I have a question about my order",
                    "I need help with returns"
                ]
            },
            {
                keywords: ['thanks', 'thank you', 'helpful'],
                response: "You're welcome! I'm glad I could help. Is there anything else you'd like to know?",
                suggestions: [
                    "Yes, I have another question",
                    "No, that's all for now"
                ]
            }
        ];
        
        // Find matching response
        for (const item of responses) {
            for (const keyword of item.keywords) {
                if (input.includes(keyword)) {
                    return {
                        message: item.response,
                        suggestions: item.suggestions
                    };
                }
            }
        }
        
        // Default response if no match found
        return {
            message: "I'm sorry, I don't have specific information about that. Would you like to contact our customer support team for more help?",
            suggestions: [
                "Contact customer support",
                "Show me your products",
                "How does shipping work?",
                "Tell me about returns"
            ]
        };
    }
}
