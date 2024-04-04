import streamlit as st
import random
import string
from PIL import Image


def main():
    st.set_page_config(
        page_title="Build Your Ascension Model", page_icon=":sparkles:", layout="wide"
    )

    # Add logo at the top
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=200)
    except FileNotFoundError:
        st.error(
            "Logo file not found. Please make sure the file 'logo.png' exists in the same directory as this script."
        )

    st.title("Build Your Ascension Model")

    # Your Business Background
    st.header("Your Business Background")
    st.write(
        "Describe your wellness business, target audience, and unique value proposition."
    )

    avatar_desc = st.text_area(
        "Ideal Client Avatar Description",
        placeholder="Example: A busy working mom in her 30s who wants to prioritize her health and well-being but struggles to find time for self-care.",
        help="Provide a detailed description of your ideal client or target audience, including their demographics, lifestyle, and main challenges or goals related to wellness.",
    )

    avatar_pain_list = st.text_area(
        "Ideal Client Pain Points",
        placeholder="Example: Time constraints, difficulty balancing work and family, feeling overwhelmed and stressed, lack of energy, unhealthy eating habits.",
        help="List the key problems, challenges, or pain points your ideal client faces in their wellness journey.",
    )

    st.write("Select your unique value proposition.")
    uvp_type = st.selectbox(
        "Unique Value Proposition Type",
        [
            "Affordability",
            "Convenience",
            "Personalization",
            "Expertise",
            "Community",
            "Holistic Approach",
            "Innovative Solutions",
            "Luxury Experience",
            "Proven Results",
            "Other",
        ],
        index=2,
    )
    unique_value_prop = st.text_area(
        "Unique Value Proposition",
        placeholder="Example: We offer personalized wellness coaching that combines nutrition, mindfulness, and lifestyle strategies to help busy moms achieve optimal health and balance, no matter how hectic their schedule.",
        help="Describe how your wellness offerings uniquely address your ideal client's needs and provide value in a way that sets you apart from competitors.",
    )

    if uvp_type == "Other":
        other_uvp_desc = st.text_area(
            "Other Unique Value Proposition",
            help="If you selected 'Other' for your unique value proposition type, please provide a brief description of what makes your wellness offerings unique and valuable to your ideal client.",
        )

    st.markdown('<hr class="stDivider">', unsafe_allow_html=True)

    # Your Menu
    st.header("Your Menu of Offerings")
    st.write(
        "Describe your wellness offerings, including lead magnets, pricing, and packages."
    )

    lead_magnet_desc = st.text_area(
        "Lead Magnet Description",
        placeholder="Example: Download our free guide: '5 Simple Self-Care Strategies for Busy Moms'",
        help="Describe your lead magnet or free offering designed to attract potential clients and encourage them to join your email list.",
    )

    st.subheader("Offer Levels")
    st.write("Select the types of wellness offerings you provide.")
    ticket_types = [
        "One time course/document",
        "Recurring membership/community/club",
        "One time Hourly Virtual",
        "One time Hourly Local",
        "Recurring/Package Hourly Virtual",
        "Recurring/Package Hourly Local",
        "One time Project Deliverable",
        "Recurring Services (Retainer)",
        "Virtual Experience/Event",
        "In Person Experience/Event/Retreat",
        "Other",
    ]
    num_ticket_items = st.number_input(
        "Number of Offerings", min_value=1, max_value=11, value=4, step=1
    )

    ticket_items = []
    for i in range(int(num_ticket_items)):
        if i < len(ticket_types):
            ticket_type = ticket_types[i]
        else:
            ticket_type = f"Additional Offer {i - len(ticket_types) + 1}"

        st.header(f"{ticket_type} Offer Details")

        product_name = st.text_input(
            f"{ticket_type} Offer Name",
            placeholder=f"Example: {ticket_type} - Wellness Transformation Package",
            help=f"Enter a clear and descriptive name for your {ticket_type.lower()} wellness offer.",
        )

        st.write(f"Select the format of your {ticket_type.lower()} wellness offer.")
        product_type = st.selectbox(
            f"{ticket_type} Offer Format",
            [
                "Online Course",
                "Ebook or Guide",
                "Coaching Program",
                "Membership Community",
                "Wellness Retreat",
                "Workshop or Seminar",
                "Physical Product",
                "Other",
            ],
            index=0,
        )

        st.write(
            f"Enter the price for your {ticket_type.lower()} wellness offer. Use the plus button to increase the price by $50."
        )
        price = st.number_input(
            f"{ticket_type} Offer Price", min_value=0, value=100, step=50
        )

        st.write(
            f"Describe what's included in your {ticket_type.lower()} wellness offer."
        )
        features_desc = st.text_area(
            f"{ticket_type} Offer Inclusions",
            placeholder="Example:\n- 6 weekly group coaching calls\n- Access to private online community\n- Personalized nutrition plan\n- Guided meditation recordings",
            help=f"Provide a detailed list of what clients will receive when they purchase your {ticket_type.lower()} wellness offer.",
        )

        st.write(
            f"Highlight the key benefits and transformations your {ticket_type.lower()} wellness offer provides."
        )
        benefits = st.text_area(
            f"{ticket_type} Offer Benefits",
            placeholder="Example:\n- Increased energy and vitality\n- Improved work-life balance\n- More restful sleep\n- Reduced stress and anxiety\n- Greater self-awareness and mindfulness",
            help=f"Clearly communicate the positive outcomes and transformations clients can expect from your {ticket_type.lower()} wellness offer.",
        )

        ticket_item = {
            "product_name": product_name,
            "product_type": product_type,
            "price": price,
            "features_desc": features_desc,
            "benefits": benefits,
        }
        ticket_items.append(ticket_item)

    # Submit Button
    submit_button = st.button("Submit")

    if submit_button:
        # Check if any default values are unchanged
        default_values_unchanged = False
        for key, value in st.session_state.items():
            if isinstance(value, str) and value.startswith("Example:"):
                default_values_unchanged = True
                break

        if default_values_unchanged:
            st.warning(
                "Please update all fields with your own information before submitting."
            )
        else:
            # Process the form data
            form_data = {
                "avatar_desc": avatar_desc,
                "avatar_pain_list": avatar_pain_list,
                "unique_value_prop": unique_value_prop,
                "uvp_type": uvp_type,
                "other_uvp_desc": other_uvp_desc if uvp_type == "Other" else None,
                "lead_magnet_desc": lead_magnet_desc,
                "num_ticket_items": num_ticket_items,
                "ticket_items": ticket_items,
            }
            st.success("Form submitted successfully!")
            st.write(form_data)


if __name__ == "__main__":
    main()
