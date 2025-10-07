import streamlit as st
from firebase_config import db
from datetime import datetime
import time

def find_user_by_iban(iban):
    """Find user by IBAN in the database"""
    try:
        users_ref = db.collection("users")
        docs = users_ref.stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            if user_data.get("iban") == iban:
                return doc.id  # Return username
        return None
    except Exception as e:
        print(f"Error finding user by IBAN: {e}")
        return None

def app():
    from utils import add_header_logo
    add_header_logo()
    st.title("💸 Send Money")
    
    # Check if user is logged in
    if "username" not in st.session_state or not st.session_state.username:
        st.error("Please log in first!")
        return
    
    user_id = st.session_state.username
    
    # Get current balance and IBAN
    try:
        balance_ref = db.collection("users").document(user_id).collection("account").document("balance")
        balance_doc = balance_ref.get()
        
        if balance_doc.exists:
            balance_data = balance_doc.to_dict()
            current_balance = balance_data.get("checking", 0)
            user_iban = balance_data.get("iban", "N/A")
            st.info(f"💰 Available Balance: ${current_balance:,.2f}")
            st.caption(f"Your IBAN: {user_iban}")
        else:
            # Initialize balance if not exists
            import random
            user_iban = f"AE{''.join([str(random.randint(0, 9)) for _ in range(8)])}"
            db.collection("users").document(user_id).collection("account").document("balance").set({
                "checking": 5000.00,
                "savings": 12430.75,
                "credit_card": 1230.00,
                "iban": user_iban
            })
            current_balance = 5000.00
            st.info(f"💰 Available Balance: ${current_balance:,.2f}")
            st.caption(f"Your IBAN: {user_iban}")
            
    except Exception as e:
        st.error(f"Error fetching balance: {e}")
        return
    
    # Fetch user's beneficiaries
    try:
        beneficiaries_ref = db.collection("users").document(user_id).collection("beneficiaries")
        docs = beneficiaries_ref.stream()
        
        beneficiaries = {}
        for doc in docs:
            data = doc.to_dict()
            beneficiaries[data['name']] = data
        
        if not beneficiaries:
            st.warning("⚠️ You haven't added any beneficiaries yet. Go to 'Add Beneficiary' first.")
            return
            
    except Exception as e:
        st.error(f"Error fetching beneficiaries: {e}")
        return
    
    # Send money form
    st.subheader("Transfer Details")
    
    beneficiary_name = st.selectbox("Select Beneficiary", list(beneficiaries.keys()))
    
    if beneficiary_name:
        beneficiary_iban = beneficiaries[beneficiary_name]['iban']
        st.text_input("IBAN", value=beneficiary_iban, disabled=True)
        
        '''trust_score = beneficiaries[beneficiary_name].get('trust_score', 'N/A')
        if isinstance(trust_score, int):
            st.text_input("Trust Score", value=f"{'⭐' * trust_score} ({trust_score}/5)", disabled=True)
        else:
            st.text_input("Trust Score", value=str(trust_score), disabled=True)'''
        
        # Check if beneficiary exists in our database
        recipient_user_id = find_user_by_iban(beneficiary_iban)
        if recipient_user_id:
            st.success(f"✅ {beneficiary_name} is a registered user - they will receive the money!")
        else:
            st.info(f"ℹ️ {beneficiary_name} is an external account")
    
    amount = st.number_input("Amount ($)", min_value=0.01, max_value=float(current_balance), step=0.01, value=0.01)
    description = st.text_input("Description (optional)", placeholder="e.g., Rent payment")
    
    if st.button("💸 Send Money", type="primary", use_container_width=True):
        if amount > current_balance:
            st.error("❌ Insufficient balance!")
        elif amount <= 0:
            st.error("❌ Amount must be greater than 0!")
        else:
            try:
                # Calculate new balance for sender
                new_balance = current_balance - amount
                
                # Update sender's balance
                balance_ref.update({"checking": new_balance})
                
                # Create transaction record for sender
                db.collection("users").document(user_id).collection("transactions").add({
                    "date": datetime.now(),
                    "type": "sent",
                    "from": user_id,
                    "to": beneficiary_name,
                    "amount": amount,
                    "balance_after": new_balance,
                    "description": description if description else f"Transfer to {beneficiary_name}"
                })
                
                # Check if recipient exists and credit their account
                recipient_user_id = find_user_by_iban(beneficiary_iban)
                if recipient_user_id:
                    # Recipient exists - credit their account
                    recipient_balance_ref = db.collection("users").document(recipient_user_id).collection("account").document("balance")
                    recipient_balance_doc = recipient_balance_ref.get()
                    
                    if recipient_balance_doc.exists:
                        recipient_balance = recipient_balance_doc.to_dict().get("checking", 0)
                        new_recipient_balance = recipient_balance + amount
                        
                        # Update recipient's balance
                        recipient_balance_ref.update({"checking": new_recipient_balance})
                        
                        # Create transaction record for recipient
                        db.collection("users").document(recipient_user_id).collection("transactions").add({
                            "date": datetime.now(),
                            "type": "received",
                            "from": user_id,
                            "to": recipient_user_id,
                            "amount": amount,
                            "balance_after": new_recipient_balance,
                            "description": description if description else f"Received from {user_id}"
                        })
                        
                        st.success(f"✅ Successfully sent ${amount:,.2f} to {beneficiary_name}!")
                        st.info(f"💰 {beneficiary_name} received the money in their account!")
                    else:
                        st.success(f"✅ Successfully sent ${amount:,.2f} to {beneficiary_name}!")
                else:
                    # External account - transaction recorded but no credit
                    st.success(f"✅ Successfully sent ${amount:,.2f} to {beneficiary_name} (External Account)!")
                
                st.info(f"💰 Your New Balance: ${new_balance:,.2f}")
                
                # Wait and refresh
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Transaction failed: {e}")