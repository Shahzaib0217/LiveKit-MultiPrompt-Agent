# agents/buying.py
from livekit.agents import Agent
from livekit.agents import function_tool
from livekit.api.twirp_client import TwirpError

from agents.base import BaseAgent, RunContext_T

class BuyingAgent(BaseAgent):
    def __init__(
        self,
        instructions: str = "You are an Iphone sales Agent. Ask customer about their needs, focus on camera, battery and phones offering both features. Recommend phones based on their interests. Then finalize the order in a professional way.",
    ):
        super().__init__(instructions=instructions)

        self.VALID_MODELS = {
            "iphone 15",
            "iphone 15 plus",
            "iphone 15 pro",
            "iphone 15 pro max",
            "iphone S E",
            "iphone 14",
            "iphone 14 plus",
            "iphone 13 mini",
        }

    @function_tool()
    async def recommend_models(
        self, features: str, context: RunContext_T
    ) -> tuple[Agent, str]:
        """
        Recommend three iPhone models based on user requirements.
        """
        print("🛠️ TOOL CALLED: Recommend models")
        features_lower = features.lower()

        # Simplified logic: pick by keyword or default
        if "camera" in features_lower:
            choices = ["iPhone 15 Pro", "iPhone 15 Pro Max", "iPhone 14 Plus"]
        elif "battery" in features_lower:
            choices = ["iPhone 15 Plus", "iPhone 15", "iPhone 14 Plus"]
        else:
            choices = ["iPhone 15", "iPhone 15 Plus", "iPhone 14 pro"]

        msg = (
            f"Based on your interest in {features}, I recommend: {', '.join(choices)}. "
            "Which one appeals to you?"
        )
        return msg


    @function_tool()
    async def set_selected_model(self, model: str, context: RunContext_T) -> tuple[Agent, str]:
        print("🛠️ TOOL CALLED: set selected model")
        model_key = model.strip().lower()
        if model_key not in self.VALID_MODELS:
            return (
                f"Sorry, I don’t recognize “{model}”. Here are our current models: "
                f"{', '.join(sorted(self.VALID_MODELS))}. Which would you like?"
            )
        context.userdata.selected_model = model.title()
        return (
            f"Great! You’ve selected the iPhone {context.userdata.selected_model}. "
            "Would you like to confirm your purchase?"
        )


    @function_tool()
    async def confirm_order_details(self, context: RunContext_T) -> tuple[Agent, str]:
        print("🛠️ TOOL CALLED: Confirm Order Details")
        model = context.userdata.selected_model
        name = context.userdata.customer_name or "Customer"
        return (
            f"Thanks, {name}! Just to recap: you’re buying an iPhone {model}. "
            "Shall I proceed to place your order?"
        )


    @function_tool()
    async def place_order(self, context: RunContext_T) -> tuple[Agent, str]:
        print("🛠️ TOOL CALLED: Place Order")
        return "Your order has been confirmed! I hope you will enjoy your time with your new Iphone."


    @function_tool()
    async def explore_more(self, context: RunContext_T) -> tuple[Agent, str]:
        print("🛠️ TOOL CALLED: Explore more")    
        """User wants to look at more options."""
        context.userdata.selected_model = None
        return "Sure, let’s look at more iPhone options. What features matter to you?"


    @function_tool()
    async def end_purchase_call(self, context: RunContext_T) -> str:
        """Called when the purchase is complete and the customer wants to end the call."""
        print("📞 TOOL CALLED: end_purchase_call - ending session")
        farewell = "Thank you for your purchase, have a wonderful day!"
        # attempt cleanup
        try:
            await self._end_session()
        except TwirpError as e:
            self.logger.warning("Could not delete room (already gone?): %s", e)
        return farewell


    @function_tool()
    async def to_support(self, context: RunContext_T) -> tuple[Agent, str]:
        """Called when customer changes their mind and wants technical support instead of buying a phone."""
        print("🔄 TOOL CALLED: to_support - customer switching from buying to support")
        return await self._transfer_to_agent("support", context)