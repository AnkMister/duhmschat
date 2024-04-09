# streamdspy1.py
import os
import streamlit as st
from supabase import create_client, Client
import dspy
from dotenv import load_dotenv

load_dotenv()
# Configure the Unify model
unify_key = os.getenv("UNIFY_API_KEY")
print(unify_key)
mixtral = dspy.OpenAI(
    api_base="https://api.unify.ai/v0/",
    api_key=unify_key,
    model="mixtral-8x7b-instruct-v0.1@together-ai",
    model_type="chat",
)
gpt35 = dspy.OpenAI(
    api_base="https://api.unify.ai/v0/",
    api_key=unify_key,
    model="gpt-3.5-turbo@openai",
    # model="mixtral-8x7b-instruct-v0.1@together-ai",
    model_type="chat",
    max_tokens=2**12,
)
dspy.settings.configure(lm=gpt35)


class BusinessAnalysis(dspy.Signature):
    """Generate a business analysis based on the provided context"""

    context = dspy.InputField(
        desc="Business background and details, including additional user input",
        format=lambda x: str(x),
    )
    topic = dspy.InputField(desc="The topic for the business analysis")
    analysis = dspy.OutputField(
        desc="A business analysis based on the provided context and topic"
    )


generate_analysis = dspy.Predict(BusinessAnalysis)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def main():
    st.set_page_config(page_title="Business Analysis Generator", layout="wide")

    st.title("Business Analysis Generator")

    # User input for email address
    email = st.text_input("Enter your email address")

    if email:
        # Query Supabase to get the row based on email
        query = (
            supabase.table("form_submissions").select("*").eq("email", email).limit(1)
        )
        result = query.execute()

        if len(result.data) > 0:
            # Display the row data in a clean format
            row_data = result.data[0]
            st.subheader("Business Information")
            st.write(f"Avatar Description: {row_data['avatar_desc']}")
            st.write(f"Avatar Pain List: {row_data['avatar_pain_list']}")
            st.write(f"Unique Value Proposition: {row_data['unique_value_prop']}")
            st.write(f"UVP Type: {row_data['uvp_type']}")
            st.write(f"UVP Proof: {row_data['uvp_proof']}")
            st.write(f"Lead Magnet Description: {row_data['lead_magnet_desc']}")
            st.write(f"Number of Ticket Items: {row_data['num_ticket_items']}")

            # Display ticket items
            st.subheader("Ticket Items")
            for i, ticket_item in enumerate(row_data["ticket_items"], start=1):
                st.write(f"Ticket Item {i}:")
                st.write(f"  Product Name: {ticket_item['product_name']}")
                st.write(f"  Product Type: {ticket_item['product_type']}")
                st.write(f"  Price: {ticket_item['price']}")
                st.write(f"  Features/Description: {ticket_item['features_desc']}")
                st.write(f"  Benefits: {ticket_item['benefits']}")

            # Additional user input
            additional_input = st.text_area("Provide additional context (optional)")

            # Topic input
            topic = st.text_input("Enter the topic for the business analysis")

            # Button to generate business analysis
            if st.button("Generate Business Analysis"):
                # Combine the row data and additional user input
                context = {
                    "row_data": row_data,
                    "additional_input": additional_input,
                }

                # Generate the business analysis using DSPy
                pred = generate_analysis(context=context, topic=topic)
                business_analysis = pred.analysis

                # Display the business analysis
                st.subheader("Business Analysis")
                st.write(business_analysis)

                # Button to save the analysis to Supabase
                if st.button("Save Analysis to Supabase"):
                    # Save the analysis to the llm_outputs table
                    supabase.table("llm_outputs").insert(
                        {
                            "email": email,
                            "context": str(context),
                            "topic": topic,
                            "analysis": business_analysis,
                        }
                    ).execute()
                    st.success("Business analysis saved to Supabase!")
        else:
            st.warning("No data found for the provided email address.")


if __name__ == "__main__":
    main()
