import streamlit as st
import openai
import os
from typing import Dict, Optional

class JargonTranslator:
    """Translate financial jargon into simple explanations"""

    def __init__(self):
        """Initialize the translator"""
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.translation_cache = {}

    def translate_text(self, text: str) -> Optional[Dict]:
        """Translate financial jargon to simple explanations"""
        try:
            # Check cache first
            if text in self.translation_cache:
                return self.translation_cache[text]

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
            self.translation_cache[text] = translation
            return translation

        except Exception as e:
            st.error(f"Error translating text: {str(e)}")
            return None

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
