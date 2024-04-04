import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
# Supabase credentials


# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_form_data_by_email(email):
    data = supabase.table("form_submissions").select("*").eq("email", email).execute()
    if data.data:
        return data.data[0]  # Return the first record that matches the email
    else:
        return None  # No data found for the email


def insert_or_update_form_data(email, form_data):
    existing_data = get_form_data_by_email(email)
    if existing_data:
        # Update existing record
        updated_data = (
            supabase.table("form_submissions")
            .update(form_data)
            .eq("email", email)
            .execute()
        )
        st.success("Form data updated successfully!")
    else:
        # Insert new record
        inserted_data = supabase.table("form_submissions").insert(form_data).execute()
        st.success("Form data inserted successfully!")


def main():
    st.set_page_config(
        page_title="Build Your Ascension Model",
        page_icon=":sparkles:",
        layout="centered",
    )

    # Set background color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #989595;
            color: black;
            font-family: Arial, sans-serif;
        }
        .stHeader {
            color: #377a81;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .stSubheader {
            color: #377a81;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .stSectionDesc {
            color: #555555;
            margin-bottom: 20px;
        }
        .stTextArea, .stTextInput {
            border-radius: 5px;
            padding: 10px;
            background-color: transparent;
            border: 0px solid #cccccc;
        }
        .stButton {
            background-color: #377a81;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
        }
        .stDivider {
            border: none;
            border-top: 1px solid #cccccc;
            margin: 30px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Add logo
    st.sidebar.image("logo.png", use_column_width=True)

    st.title("Build Your Ascension Model")

    email = st.text_input("Email Address", key="email")
    st.markdown(
        '<p class="stSubHeader">Enter the email address you used to sign up to Wellness Code</p>',
        unsafe_allow_html=True,
    )

    # Your Business Background
    st.markdown(
        '<p class="stHeader">Your Business Background</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="stSectionDesc">Describe your business, target audience, and unique value proposition.</p>',
        unsafe_allow_html=True,
    )

    avatar_desc = st.text_area(
        "Avatar Description",
        value="Example: A busy working mom seeking inner peace and balance.",
        key="avatar_desc",
    )

    avatar_pain_list = st.text_area(
        "Avatar Problem/Pain List",
        value="Example: Lack of time, difficulty balancing work and family, feeling overwhelmed.",
        key="avatar_pain_list",
    )

    st.write("")
    st.markdown(
        '<p class="stSectionDesc">Pick your unique value proposition.</p>',
        unsafe_allow_html=True,
    )
    uvp_type = st.selectbox(
        "",
        [
            "Cheaper",
            "Bespoke",
            "White-Glove",
            "Luxury",
            "Niche",
            "Convenience",
            "Expertise",
            "Exclusivity",
            "Customization",
            "Other",
        ],
        index=2,
        key="uvp_type",
    )
    unique_value_prop = st.text_area(
        "Unique Value Proposition",
        value="Example: Our holistic approach combines ancient wisdom with modern mindfulness techniques, tailored specifically for busy professionals seeking inner peace and balance.",
        key="unique_value_prop",
    )

    other_uvp_desc = st.text_area(
        "Unique Value Proposition Description", key="uvp_desc"
    )

    st.markdown('<hr class="stDivider">', unsafe_allow_html=True)

    # Your Menu
    st.markdown('<p class="stHeader">Your Menu</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="stSectionDesc">Describe your offerings, including lead magnets, pricing, and packages.</p>',
        unsafe_allow_html=True,
    )

    lead_magnet_desc = st.text_area(
        "Lead Magnet Description",
        value="Example: Download our free guided meditation for inner peace.",
        key="lead_magnet_desc",
    )

    st.markdown(
        '<p class="stSubheader">Number of Offerings</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="stSectionDesc">Select the number of offerings or packages you want to present.</p>',
        unsafe_allow_html=True,
    )
    num_ticket_items = st.number_input(
        "", min_value=3, max_value=5, value=3, step=1, key="num_ticket_items"
    )

    ticket_names = ["Low Ticket", "Medium Ticket", "High Ticket"]
    if num_ticket_items > 3:
        ticket_names.append("Additional Offer A")
    if num_ticket_items > 4:
        ticket_names.append("Additional Offer B")

    st.markdown('<p class="stSubheader">Offer Order</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="stSectionDesc">Drag and drop the offerings to set the order in which they increase in price.</p>',
        unsafe_allow_html=True,
    )
    ticket_order = st.multiselect("", ticket_names, ticket_names, key="ticket_order")

    st.markdown('<hr class="stDivider">', unsafe_allow_html=True)

    # Ticket Items
    ticket_items = []
    for ticket_name in ticket_order:
        st.markdown(
            f'<p class="stSubheader">{ticket_name} Offer</p>', unsafe_allow_html=True
        )

        # Product Name
        st.write(f"Enter the name of your {ticket_name.lower()} offering or package.")
        product_name = st.text_input(
            f"{ticket_name} Offer Name",
            value=f"Example: {ticket_name} Awakening Journey",
            key=f"product_name_{ticket_name}",
        )

        # Product Type
        st.write(f"Select the type of {ticket_name.lower()} offering or package.")
        product_type = st.selectbox(
            f"{ticket_name} Offer Type",
            [
                "Online Course",
                "Membership Community",
                "Virtual Coaching",
                "In-Person Coaching",
                "Virtual Retreat",
                "In-Person Retreat",
                "Other",
            ],
            index=0,
            key=f"product_type_{ticket_name}",
        )

        # Price
        st.write(
            f"Enter the price for {ticket_name} Offer. Use the plus button to increase the price by $50."
        )
        price = st.number_input(
            f"{ticket_name} Offer Price",
            min_value=0,
            value=100,
            step=50,
            key=f"price_{ticket_name}",
        )

        # Features/Description
        st.write(f"Enter the features and description for {ticket_name} Offer.")
        features_desc = st.text_area(
            f"{ticket_name} Offer Features/Description",
            value="Example: - 6 video modules\n- Workbook and guided meditations\n- Private community access",
            key=f"features_desc_{ticket_name}",
        )

        # Benefits
        st.write(f"Enter the benefits for {ticket_name} Offer.")
        benefits = st.text_area(
            f"{ticket_name} Offer Benefits",
            value="Example: - Achieve inner peace and balance\n- Reduce stress and anxiety\n- Cultivate mindfulness and presence",
            key=f"benefits_{ticket_name}",
        )

        ticket_item = {
            "product_name": product_name,
            "product_type": product_type,
            "price": price,
            "features_desc": features_desc,
            "benefits": benefits,
        }
        ticket_items.append(ticket_item)
    # ... (rest of the code remains unchanged until the submit button logic)

    # Submit Button
    submit_button = st.button("Submit", key="submit_button")

    if submit_button:
        # Check if any default values are unchanged

        default_values_unchanged = False
        for key, value in st.session_state.items():
            if isinstance(value, str) and value.startswith("Example:"):
                default_values_unchanged = False  # temporary
                break

        if default_values_unchanged:
            st.warning(
                "Please update all fields with your own information before submitting."
            )
        else:
            # Process the form data
            form_data = {
                "email": st.session_state.get(
                    "email"
                ),  # Assuming email is collected elsewhere in the form
                "avatar_desc": avatar_desc,
                "avatar_pain_list": avatar_pain_list,
                "unique_value_prop": unique_value_prop,
                "uvp_type": uvp_type,
                "other_uvp_desc": other_uvp_desc,
                "lead_magnet_desc": lead_magnet_desc,
                "num_ticket_items": num_ticket_items,
                "ticket_order": ticket_order,
                "ticket_items": ticket_items,
            }
            # Insert or update form data in Supabase
            insert_or_update_form_data(form_data["email"], form_data)
            st.success("Form submitted successfully")


if __name__ == "__main__":
    main()
