from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from typing import Dict, Any
import json

from database.db_manager import DatabaseManager

def debug_print(class_name: str, function_name: str, detail: str):
    print(f"[bot][{class_name}][{function_name}] {detail}")

# Conversation states
EMAIL = 0
INDUSTRY = 1
LOCATION = 2
CAMPAIGN_PARAMS = 3

class OnboardingBot:
    def __init__(self, token: str):
        """Initialize the onboarding bot."""
        self.token = token
        self.app = Application.builder().token(token).build()
        debug_print("OnboardingBot", "__init__", f"Initializing bot")
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up conversation handlers for onboarding flow."""
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_email)],
                INDUSTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_industry)],
                LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_location)],
                CAMPAIGN_PARAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_campaign_params)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )
        self.app.add_handler(conv_handler)
        debug_print("OnboardingBot", "_setup_handlers", "Handlers configured")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start the onboarding conversation."""
        user = update.effective_user
        user_id = str(user.id)
        telegram_handle = user.username
        
        # Use user ID if no username is set
        client_id = telegram_handle if telegram_handle else user_id
        display_name = f"@{telegram_handle}" if telegram_handle else f"User {user_id}"
        
        debug_print("OnboardingBot", "start", f"Starting onboarding for {display_name}")
        
        # Store user info in context
        context.user_data['client_id'] = client_id
        context.user_data['display_name'] = display_name
        
        # Initialize database for this client
        db = DatabaseManager(client_id)
        
        await update.message.reply_text(
            f"Welcome to Gorilla7, {display_name}!\n"
            "Let's get you set up.\n\n"
            "Please provide your email address."
        )
        return EMAIL

    async def handle_email(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle email collection."""
        context.user_data['email'] = update.message.text
        debug_print("OnboardingBot", "handle_email", 
                   f"Email for {context.user_data['display_name']}: {update.message.text}")
        
        await update.message.reply_text(
            "What industry are you targeting?"
        )
        return INDUSTRY

    async def handle_industry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle industry collection."""
        context.user_data['industry'] = update.message.text
        debug_print("OnboardingBot", "handle_industry", 
                   f"Industry for {context.user_data['display_name']}: {update.message.text}")
        
        await update.message.reply_text(
            "What's your target location/region?"
        )
        return LOCATION

    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle location collection."""
        context.user_data['location'] = update.message.text
        debug_print("OnboardingBot", "handle_location", 
                   f"Location for {context.user_data['display_name']}: {update.message.text}")
        
        await update.message.reply_text(
            "Finally, let's set up your campaign parameters.\n"
            "Please provide the following in JSON format:\n"
            "{\n"
            '    "iteration_count": number,\n'
            '    "search_depth": number,\n'
            '    "lead_quantity": number\n'
            "}"
        )
        return CAMPAIGN_PARAMS

    async def handle_campaign_params(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle campaign parameters collection and complete onboarding."""
        try:
            campaign_params = json.loads(update.message.text)
            debug_print("OnboardingBot", "handle_campaign_params", 
                       f"Campaign params for {context.user_data['display_name']}: {campaign_params}")
            
            # Create client in database
            db = DatabaseManager(context.user_data['client_id'])
            success = db.create_client(
                telegram_handle=context.user_data['display_name'],
                email=context.user_data['email'],
                industry=context.user_data['industry'],
                location=context.user_data['location'],
                campaign_parameters=campaign_params
            )
            
            if success:
                await update.message.reply_text(
                    "🎉 Onboarding complete! Your campaign is ready to start.\n"
                    "Use /status to check your campaign progress."
                )
            else:
                await update.message.reply_text(
                    "⚠️ There was an issue creating your profile. Please try again with /start"
                )
            
            return ConversationHandler.END
            
        except json.JSONDecodeError:
            await update.message.reply_text(
                "Invalid JSON format. Please try again with the correct format:\n"
                "{\n"
                '    "iteration_count": number,\n'
                '    "search_depth": number,\n'
                '    "lead_quantity": number\n'
                "}"
            )
            return CAMPAIGN_PARAMS

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel the conversation."""
        display_name = context.user_data.get('display_name', f"User {update.effective_user.id}")
        debug_print("OnboardingBot", "cancel", f"Onboarding cancelled for {display_name}")
        await update.message.reply_text("Onboarding cancelled. Use /start to begin again.")
        return ConversationHandler.END

    def run(self):
        """Run the bot."""
        debug_print("OnboardingBot", "run", "Starting bot")
        self.app.run_polling()
