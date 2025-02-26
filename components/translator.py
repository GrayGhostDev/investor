import streamlit as st
import openai
import os
import json
import random
from typing import Dict, Optional

class JargonTranslator:
    """Translate financial jargon into simple explanations"""

    def __init__(self):
        """Initialize the translator"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                self.api_available = True
            except Exception as e:
                st.warning(f"Error initializing OpenAI client: {str(e)}")
                self.api_available = False
        else:
            st.warning("OpenAI API key not set. Translator will use mock responses.")
            self.api_available = False
            
        self.translation_cache = {}

    def _generate_mock_translation(self, text: str) -> Dict:
        """Generate mock translation data when API is not available"""
        # Common financial terms with simple explanations
        financial_terms = {
            "convertible note": {
                "simple_explanation": "A convertible note is a short-term loan that converts into equity (ownership) in a company, typically during a future funding round.",
                "key_terms": {
                    "Conversion": "The process of changing the loan into company shares",
                    "Valuation Cap": "The maximum company value at which the note converts to equity",
                    "Discount Rate": "A reduced price for converting compared to what new investors pay"
                },
                "example": "If you invest $50,000 through a convertible note, it might later convert to shares worth $75,000 if the company does well.",
                "context": "Convertible notes are popular for early-stage startups because they delay establishing a company valuation until more data is available."
            },
            "pro-rata rights": {
                "simple_explanation": "Pro-rata rights allow investors to invest additional money in future funding rounds to maintain their percentage ownership in the company.",
                "key_terms": {
                    "Dilution": "The reduction in ownership percentage when new shares are issued",
                    "Participation Right": "The option to invest more to maintain ownership percentage",
                    "Ownership Stake": "The percentage of a company that an investor owns"
                },
                "example": "If you own 5% of a company and have pro-rata rights, you can invest enough in the next round to keep that 5% ownership.",
                "context": "Pro-rata rights are valuable because they protect investors from having their ownership percentage reduced when new investors join."
            },
            "liquidation preference": {
                "simple_explanation": "Liquidation preference determines who gets paid first and how much when a company is sold or goes bankrupt.",
                "key_terms": {
                    "1x Preference": "Getting your original investment back before others get paid",
                    "Participating": "Getting your money back AND sharing in the remaining proceeds",
                    "Non-participating": "Having to choose between getting your preference OR converting to common shares"
                },
                "example": "With a 1x non-participating preference, if you invested $1 million, you'd get the first $1 million from a sale, or you could convert to common shares if that would give you more.",
                "context": "Liquidation preferences protect investors in downside scenarios, ensuring they recover some or all of their investment before others get paid."
            }
        }
        
        # Check if the input text contains any of our known terms
        text_lower = text.lower()
        for term, explanation in financial_terms.items():
            if term in text_lower:
                return explanation
        
        # If no specific term is found, generate a generic response
        return {
            "simple_explanation": f"This is a simplified explanation of '{text}'. Financial terms can be complex, but this breaks it down into everyday language.",
            "key_terms": {
                "Term 1": "A simple definition of the first important term",
                "Term 2": "A simple definition of the second important term"
            },
            "example": "Here's a practical example of how this concept works in real life.",
            "context": "This is some additional background information to help understand the concept better."
        }

    def translate_text(self, text: str) -> Optional[Dict]:
        """Translate financial jargon to simple explanations"""
        try:
            # Check cache first
            if text in self.translation_cache:
                return self.translation_cache[text]
                
            # Use mock data if API is not available
            if not self.api_available:
                mock_translation = self._generate_mock_translation(text)
                self.translation_cache[text] = mock_translation
                return mock_translation

            prompt = f"""
            Translate this financial or investment-related text into simple, clear language:
            "{text}"

            Provide a JSON response with:
            1. Simple explanation
            2. Key terms defined
            3. Example if applicable
            4. Additional context (if needed)

            Format as JSON with these keys:
            simple_explanation, key_terms, example, context
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at explaining complex financial concepts simply."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            translation = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                translation_dict = json.loads(translation)
                self.translation_cache[text] = translation_dict
                return translation_dict
            except json.JSONDecodeError:
                st.error("Error parsing translation response")
                return self._generate_mock_translation(text)

        except Exception as e:
            st.error(f"Error translating text: {str(e)}")
            return self._generate_mock_translation(text)

def render_translator_section():
    """Render the jargon translator section"""
    st.header("Financial Jargon Translator")

    # Add description
    st.markdown("""
    Need help understanding complex financial terms? 
    Paste any financial text below for a clear, simple explanation.
    """)

    # Initialize translator
    translator = JargonTranslator()

    # Text input
    financial_text = st.text_area(
        "Enter financial text to translate",
        placeholder="Example: Series A preferred stock with pro-rata rights and a 1x non-participating liquidation preference",
        help="Paste any complex financial terms or phrases here"
    )

    # Quick examples
    st.markdown("### Quick Examples")
    example_terms = [
        "Convertible Note",
        "Pro-rata Rights",
        "Post-money Valuation",
        "Down Round Protection"
    ]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Term: Convertible Note"):
            financial_text = "Convertible Note"
            st.session_state.selected_term = financial_text
    with col2:
        if st.button("Term: Pro-rata Rights"):
            financial_text = "Pro-rata Rights"
            st.session_state.selected_term = financial_text

    # Add translate button
    if st.button("Translate", type="primary") and financial_text:
        with st.spinner("Translating..."):
            translation = translator.translate_text(financial_text)
            
            if translation:
                # Display translation in an organized way
                st.success("Translation complete! 🎯")
                
                # Simple explanation
                st.subheader("Simple Explanation")
                st.write(translation["simple_explanation"])
                
                # Key terms
                st.subheader("Key Terms")
                for term, definition in translation["key_terms"].items():
                    st.markdown(f"**{term}**: {definition}")
                
                # Example
                if translation.get("example"):
                    st.subheader("Example")
                    st.write(translation["example"])
                
                # Additional context
                if translation.get("context"):
                    st.subheader("Additional Context")
                    st.write(translation["context"])

    # Add helpful tips
    with st.expander("💡 Tips for using the translator"):
        st.markdown("""
        - Paste specific terms or entire paragraphs
        - Click example terms to see instant translations
        - The translator learns from context, so include relevant details
        - Save translations for future reference
        """)
