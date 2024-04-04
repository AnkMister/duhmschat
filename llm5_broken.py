# streamdspy1.py
import os
import streamlit as st
import asyncio
from supabase import create_client, Client
import dspy
from dotenv import load_dotenv

load_dotenv()
# Configure the Unify model

unify_key = os.getenv("UNIFY_API_KEY")
print(unify_key)
unify_model = dspy.OpenAI(
    api_base="https://api.unify.ai/v0/",
    api_key=unify_key,
    model="mixtral-8x7b-instruct-v0.1@together-ai",
    model_type="chat",
)
dspy.settings.configure(lm=unify_model)


class BusinessSummary(dspy.Signature):
    """Generate a copywriting business breakdown based on the business background and details"""

    form_data = dspy.InputField(
        desc="Business Background and details coming from Supabase form data",
        format=lambda x: str(x),
    )
    summary = dspy.OutputField(
        desc="A copywriting breakdown of a business and its menu in a voice to target the brand"
    )


generate_summary = dspy.Predict(BusinessSummary)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def generate_business_summary(row_data):
    pred = await generate_summary(form_data=row_data)
    return pred.summary


async def save_summary_to_supabase(email, business_summary):
    await supabase.table("business_summaries").insert(
        {"email": email, "summary": business_summary}
    ).execute()


def main():
    st.set_page_config(page_title="Business Summary Generator", layout="wide")

    # Initialize Supabase client

    st.title("Business Summary Generator")

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
            st.write(f"Other UVP Description: {row_data['other_uvp_desc']}")
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

            # Button to generate business summary

            if st.button("Generate Funnel Output"):
                # Generate the business summary using DSPy
                business_summary = asyncio.run(generate_business_summary(row_data))

                # Display the business summary
                st.subheader("Business Summary")
                st.write(business_summary)

                # Button to save the business summary to Supabase
                if st.button("Save Business Summary"):
                    asyncio.run(save_summary_to_supabase(email, business_summary))
                    st.success("Business summary saved to Supabase!")
        else:
            st.warning("No data found for the provided email address.")


if __name__ == "__main__":
    main()
