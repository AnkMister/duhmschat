# streamdspy1.py
import streamlit as st
from supabase import create_client, Client
import dspy

# Configure the Unify model
unify_model = dspy.OpenAI(
    api_base="https://api.unify.ai/v0/",
    api_key="APIKEY",
    model="mixtral-8x7b-instruct-v0.1@together-ai",
    model_type="chat",
)
dspy.settings.configure(lm=unify_model)


class BusinessSummary(dspy.Signature):
    """Generate a business summary based on the form data"""

    form_data = dspy.InputField(desc="The form data from the Supabase database")
    summary = dspy.OutputField(desc="A business summary generated from the form data")


generate_summary = dspy.Predict(BusinessSummary)


def main():
    st.set_page_config(page_title="Business Summary Generator", layout="wide")

    # Initialize Supabase client
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    supabase = create_client(url, key)

    st.title("Business Summary Generator")

    # User input for email address
    email = st.text_input("Enter your email address")

    if email:
        # Query Supabase to get the row based on email
        query = (
            supabase.table("your_table_name").select("*").eq("email", email).limit(1)
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
            if st.button("Generate Business Summary"):
                # Generate the business summary using DSPy
                pred = generate_summary(form_data=row_data)
                business_summary = pred.summary

                # Display the business summary
                st.subheader("Business Summary")
                st.markdown(business_summary)

                # Save the business summary to Supabase
                supabase.table("business_summaries").insert(
                    {"email": email, "summary": business_summary}
                ).execute()
                st.success("Business summary generated and saved to Supabase!")
        else:
            st.warning("No data found for the provided email address.")


if __name__ == "__main__":
    main()
