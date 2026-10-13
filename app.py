
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from google import genai

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="SalesPilot AI",
    page_icon="🚀",
    layout="wide",
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
SAMPLE_LEADS = [
    {
        "id": 1,
        "customer": "Ananya Sharma",
        "company": "Urban Boutique",
        "industry": "Retail",
        "email": "ananya@urbanboutique.example",
        "subject": "Interested in your premium collection",
        "message": "Hi, we are looking for a supplier for our new premium clothing collection. Could you share your product catalogue and bulk pricing?",
        "history": [
            {
                "sender": "Customer",
                "message": "Hi, we are looking for a supplier for our new premium clothing collection. Could you share your product catalogue and bulk pricing?",
            }
        ],
        "status": "New Lead",
        "value": 45000,
        "score": 85,
        "priority": "High",
    },
    {
        "id": 2,
        "customer": "Rahul Verma",
        "company": "BrightTech Solutions",
        "industry": "Technology",
        "email": "rahul@brighttech.example",
        "subject": "Need a software demonstration",
        "message": "We are interested in your software solution. Can we schedule a demo this week? Please share available timings.",
        "history": [
            {
                "sender": "Customer",
                "message": "We are interested in your software solution. Can we schedule a demo this week? Please share available timings.",
            }
        ],
        "status": "Contacted",
        "value": 120000,
        "score": 92,
        "priority": "High",
    },
    {
        "id": 3,
        "customer": "Meera Krishnan",
        "company": "Green Homes",
        "industry": "Real Estate",
        "email": "meera@greenhomes.example",
        "subject": "Request for a project quotation",
        "message": "We would like a quotation for your services for an upcoming residential project. Please let us know what information you need.",
        "history": [
            {
                "sender": "Customer",
                "message": "We would like a quotation for your services for an upcoming residential project. Please let us know what information you need.",
            }
        ],
        "status": "Qualified",
        "value": 250000,
        "score": 78,
        "priority": "Medium",
    },
    {
        "id": 4,
        "customer": "Arjun Patel",
        "company": "Growth Media",
        "industry": "Marketing",
        "email": "arjun@growthmedia.example",
        "subject": "Following up on your proposal",
        "message": "Thank you for your proposal. Could you explain the deliverables and expected timeline before we make a decision?",
        "history": [
            {
                "sender": "Customer",
                "message": "Thank you for your proposal. Could you explain the deliverables and expected timeline before we make a decision?",
            }
        ],
        "status": "Proposal Sent",
        "value": 80000,
        "score": 72,
        "priority": "Medium",
    },
    {
        "id": 5,
        "customer": "Priya Nair",
        "company": "Metro Supplies",
        "industry": "Manufacturing",
        "email": "priya@metrosupplies.example",
        "subject": "Bulk order enquiry",
        "message": "We may need a bulk order next month. Do you offer discounts for large orders, and what is the usual delivery time?",
        "history": [
            {
                "sender": "Customer",
                "message": "We may need a bulk order next month. Do you offer discounts for large orders, and what is the usual delivery time?",
            }
        ],
        "status": "New Lead",
        "value": 65000,
        "score": 80,
        "priority": "High",
    },
]

if "leads" not in st.session_state:
    st.session_state.leads = SAMPLE_LEADS

if "selected_lead_id" not in st.session_state:
    st.session_state.selected_lead_id = 1

if "drafts" not in st.session_state:
    st.session_state.drafts = {}

if "last_generated" not in st.session_state:
    st.session_state.last_generated = {}

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def get_lead(lead_id):
    for lead in st.session_state.leads:
        if lead["id"] == lead_id:
            return lead
    return None


def money(amount):
    return f"₹{amount:,.0f}"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def ask_gemini(prompt):
    """Generate text with Gemini. Return an error if unavailable."""
    try:
        client = get_gemini_client()

        if client is None:
            return None, (
                "GEMINI_API_KEY is not set. Set your API key in the "
                "VS Code terminal, then restart the app."
            )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )

        answer = getattr(response, "text", None)
        if answer and answer.strip():
            return answer.strip(), None

        return None, "Gemini returned an empty response. Please try again."

    except Exception as error:
        return None, f"Gemini request failed: {str(error)[:350]}"


def local_reply(lead, product, company_name, tone):
    """Local fallback when the Gemini service is unavailable."""
    tone_line = {
        "Professional": "Thank you for reaching out to us.",
        "Friendly": "Thank you so much for getting in touch!",
        "Persuasive": "Thank you for your interest. We'd love to help you find the right solution.",
    }.get(tone, "Thank you for reaching out to us.")

    return (
        f"Subject: Re: {lead['subject']}\n\n"
        f"Hi {lead['customer'].split()[0]},\n\n"
        f"{tone_line}\n\n"
        f"We'd be happy to discuss {product} and understand your requirements. "
        f"Could you share a little more about your needs and preferred timeline? "
        f"We can then suggest suitable options and provide the relevant details.\n\n"
        f"Please let us know a convenient time to connect.\n\n"
        f"Best regards,\n{company_name} Sales Team"
    )


def build_reply_prompt(lead, product, company_name, tone, instructions=""):
    history_text = "\n".join(
        f"{item['sender']}: {item['message']}"
        for item in lead["history"]
    )

    return f"""
You are SalesPilot AI, a helpful sales assistant.

Write a ready-to-edit email reply to the customer's latest message.

Company: {company_name}
Product or service: {product}
Industry: {lead['industry']}
Customer: {lead['customer']}
Customer company: {lead['company']}
Customer email: {lead['email']}
Email subject: {lead['subject']}
Preferred tone: {tone}

Conversation history:
{history_text}

Additional instructions:
{instructions if instructions else "No additional instructions."}

Requirements:
- Reply to the customer's latest question directly.
- Personalize the message using relevant details.
- Keep the email concise, professional, and natural.
- Include a subject line, greeting, body, and sign-off.
- Do not invent prices, discounts, delivery dates, guarantees, or product features.
- If information is missing, say the sales team can confirm it.
- Return only the email draft, without explanations or markdown code fences.
"""


def make_reply(lead, product, company_name, tone):
    prompt = build_reply_prompt(
        lead, product, company_name, tone
    )
    answer, error = ask_gemini(prompt)

    if answer:
        st.session_state.last_generated[lead["id"]] = "Gemini AI"
        return answer, None

    st.session_state.last_generated[lead["id"]] = "Local fallback"
    return local_reply(lead, product, company_name, tone), error


def edit_reply(lead, product, company_name, tone, draft, instructions):
    prompt = f"""
You are an expert sales email editor.

Customer: {lead['customer']}
Customer company: {lead['company']}
Product or service: {product}
Company: {company_name}
Preferred tone: {tone}

Current email draft:
{draft}

User's editing instructions:
{instructions}

Rewrite the complete email following the instructions.
Keep the customer's original request in mind.
Do not invent prices, dates, promises, or unsupported product details.
Return only the revised email, with no explanation.
"""
    return ask_gemini(prompt)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
st.sidebar.title("🚀 SalesPilot AI")
st.sidebar.caption("Your AI-powered sales assistant")

company_name = st.sidebar.text_input(
    "Your company name",
    value="SalesPilot Demo Company",
)

product = st.sidebar.text_input(
    "Product or service",
    value="our products and services",
)

industry = st.sidebar.selectbox(
    "Business industry",
    [
        "Retail",
        "Technology",
        "Real Estate",
        "Marketing",
        "Manufacturing",
        "Other",
    ],
)

tone = st.sidebar.selectbox(
    "Email tone",
    ["Professional", "Friendly", "Persuasive"],
)

st.sidebar.divider()
st.sidebar.subheader("AI connection")

if os.getenv("GEMINI_API_KEY", "").strip():
    st.sidebar.success("API key detected")
else:
    st.sidebar.warning("API key not detected")

st.sidebar.caption(
    "This demo uses sample leads. It does not connect to a real "
    "mailbox or send emails."
)

# --------------------------------------------------
# HEADER AND METRICS
# --------------------------------------------------
st.title("🚀 SalesPilot AI")
st.write(
    "Manage leads, understand customer enquiries, and create "
    "personalized sales replies from one workspace."
)

leads = st.session_state.leads
total_leads = len(leads)
pipeline_value = sum(lead["value"] for lead in leads)
high_priority = sum(
    lead["priority"] == "High" for lead in leads
)
new_leads = sum(
    lead["status"] == "New Lead" for lead in leads
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Leads", total_leads)
m2.metric("Pipeline Value", money(pipeline_value))
m3.metric("High Priority", high_priority)
m4.metric("New Leads", new_leads)

st.divider()

# --------------------------------------------------
# MAIN TABS
# --------------------------------------------------
inbox_tab, crm_tab, reply_tab = st.tabs(
    ["📩 Sales Inbox", "📊 CRM Dashboard", "✍️ Reply Studio"]
)

# --------------------------------------------------
# SALES INBOX
# --------------------------------------------------
with inbox_tab:
    left, right = st.columns([1, 2])

    with left:
        st.subheader("Customer enquiries")
        search = st.text_input(
            "Search customers",
            placeholder="Search name or company...",
            key="inbox_search",
        )

        filtered_leads = [
            lead for lead in st.session_state.leads
            if search.lower() in lead["customer"].lower()
            or search.lower() in lead["company"].lower()
            or search.lower() in lead["subject"].lower()
        ]

        if not filtered_leads:
            st.info("No matching leads found.")

        for lead in filtered_leads:
            label = (
                f"{lead['customer']} · {lead['company']}\n"
                f"{lead['subject']}"
            )
            if st.button(
                label,
                key=f"select_{lead['id']}",
                width="stretch",
            ):
                st.session_state.selected_lead_id = lead["id"]

    with right:
        lead = get_lead(st.session_state.selected_lead_id)

        if lead is None:
            st.info("Select a customer to view their enquiry.")
        else:
            st.subheader(lead["company"])
            st.caption(
                f"Customer: {lead['customer']} · "
                f"{lead['email']}"
            )

            c1, c2, c3 = st.columns(3)
            c1.metric("Lead Score", f"{lead['score']}/100")
            c2.metric("Estimated Value", money(lead["value"]))
            c3.metric("Priority", lead["priority"])

            st.markdown(f"**Subject:** {lead['subject']}")
            st.markdown("**Conversation history**")

            for message in lead["history"]:
                with st.chat_message(
                    "user" if message["sender"] == "Customer" else "assistant"
                ):
                    st.caption(message["sender"])
                    st.write(message["message"])

            st.markdown("**Generate a personalized reply**")

            if st.button(
                "✨ Generate Reply with Gemini",
                key=f"generate_{lead['id']}",
                type="primary",
                width="stretch",
            ):
                with st.spinner("Preparing your reply..."):
                    generated, error = make_reply(
                        lead, product, company_name, tone
                    )
                    st.session_state.drafts[lead["id"]] = generated

                if error:
                    st.warning(
                        "Gemini could not generate a reply, so a local "
                        "fallback draft was created. "
                        + error
                    )
                else:
                    st.success("Reply generated with Gemini AI.")

            draft = st.session_state.drafts.get(lead["id"], "")

            if draft:
                st.text_area(
                    "Editable email draft",
                    key=f"draft_view_{lead['id']}",
                    value=draft,
                    height=260,
                    disabled=True,
                )

                if st.button(
                    "Open this draft in Reply Studio",
                    key=f"open_reply_{lead['id']}",
                    width="stretch",
                ):
                    st.session_state.selected_lead_id = lead["id"]
                    st.info(
                        "Open the Reply Studio tab above to edit this draft."
                    )

                st.caption(
                    "Draft source: "
                    + st.session_state.last_generated.get(
                        lead["id"], "Generated draft"
                    )
                )

# --------------------------------------------------
# CRM DASHBOARD
# --------------------------------------------------
with crm_tab:
    st.subheader("Lead pipeline")

    df = pd.DataFrame([
        {
            "Customer": lead["customer"],
            "Company": lead["company"],
            "Industry": lead["industry"],
            "Status": lead["status"],
            "Priority": lead["priority"],
            "Lead Score": lead["score"],
            "Estimated Value (₹)": lead["value"],
        }
        for lead in st.session_state.leads
    ])

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )

    st.subheader("Pipeline by status")
    status_counts = (
        df["Status"].value_counts().rename_axis("Status")
        .reset_index(name="Number of Leads")
    )

    st.bar_chart(
        status_counts.set_index("Status"),
        width="stretch",
    )

    st.subheader("Update lead status")
    selected_for_update = st.selectbox(
        "Choose a lead",
        options=st.session_state.leads,
        format_func=lambda x: f"{x['customer']} — {x['company']}",
        key="crm_lead_select",
    )

    new_status = st.selectbox(
        "New status",
        [
            "New Lead",
            "Contacted",
            "Qualified",
            "Proposal Sent",
            "Negotiation",
            "Won",
            "Lost",
        ],
        index=[
            "New Lead",
            "Contacted",
            "Qualified",
            "Proposal Sent",
            "Negotiation",
            "Won",
            "Lost",
        ].index(selected_for_update["status"])
        if selected_for_update["status"] in [
            "New Lead",
            "Contacted",
            "Qualified",
            "Proposal Sent",
            "Negotiation",
            "Won",
            "Lost",
        ] else 0,
    )

    if st.button("Save Lead Status", type="primary"):
        selected_for_update["status"] = new_status
        st.success(
            f"Updated {selected_for_update['customer']} to {new_status}."
        )
        st.rerun()

    st.download_button(
        "⬇️ Export CRM as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="salespilot_leads.csv",
        mime="text/csv",
        width="stretch",
    )

# --------------------------------------------------
# REPLY STUDIO
# --------------------------------------------------
with reply_tab:
    st.subheader("✍️ AI Reply Studio")
    st.write(
        "Generate a new email or refine a draft using plain-language instructions."
    )

    selected_lead = get_lead(st.session_state.selected_lead_id)

    if selected_lead is None:
        selected_lead = st.session_state.leads[0]

    reply_customer = st.selectbox(
        "Customer",
        options=st.session_state.leads,
        index=next(
            (
                i for i, item in enumerate(st.session_state.leads)
                if item["id"] == selected_lead["id"]
            ),
            0,
        ),
        format_func=lambda x: f"{x['customer']} — {x['company']}",
        key="reply_customer_select",
    )

    existing_draft = st.session_state.drafts.get(
        reply_customer["id"], ""
    )

    if not existing_draft:
        existing_draft = local_reply(
            reply_customer, product, company_name, tone
        )

    edited_draft = st.text_area(
        "Email draft (you can edit this directly)",
        value=existing_draft,
        height=300,
        key=f"reply_editor_{reply_customer['id']}",
    )

    instructions = st.text_input(
        "How should the AI improve it?",
        placeholder="e.g. Make it shorter, warmer, and ask for a meeting",
    )

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button(
            "✨ Improve with Gemini",
            type="primary",
            width="stretch",
        ):
            if not instructions.strip():
                st.warning(
                    "Enter an editing instruction first."
                )
            else:
                with st.spinner("Improving your email..."):
                    revised, error = edit_reply(
                        reply_customer,
                        product,
                        company_name,
                        tone,
                        edited_draft,
                        instructions,
                    )

                if revised:
                    st.session_state.drafts[reply_customer["id"]] = revised
                    st.session_state.last_generated[
                        reply_customer["id"]
                    ] = "Gemini AI"
                    st.success(
                        "Revised draft saved. The updated draft appears "
                        "after the app refreshes."
                    )
                    st.rerun()
                else:
                    st.error(error or "Could not improve the draft.")

    with col_b:
        if st.button(
            "Save my edits",
            width="stretch",
        ):
            st.session_state.drafts[
                reply_customer["id"]
            ] = edited_draft
            st.session_state.last_generated[
                reply_customer["id"]
            ] = "User edited"
            st.success("Your draft has been saved.")

    st.download_button(
        "⬇️ Download email draft",
        data=edited_draft,
        file_name=f"sales_reply_{reply_customer['id']}.txt",
        mime="text/plain",
        width="stretch",
    )

    st.info(
        "This is a prototype: drafts are not sent to customers. "
        "The inbox contains fictional demo messages."
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption(
    f"SalesPilot AI · Demo workspace · "
    f"Last refreshed {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
)
