from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
from google.analytics.admin_v1beta.types import ListAccountsRequest, ListPropertiesRequest
from google.oauth2.credentials import Credentials

def list_properties(access_token):
    creds = Credentials(token=access_token)
    client = AnalyticsAdminServiceClient(credentials=creds)
    
    # List all accounts
    accounts_request = ListAccountsRequest()
    accounts = client.list_accounts(request=accounts_request)
    
    properties = []
    for account in accounts:
        account_id = account.name.split("/")[-1]
        
        # List properties for this account
        prop_request = ListPropertiesRequest(filter=f"parent:accounts/{account_id}")
        prop_response = client.list_properties(request=prop_request)
        
        for prop in prop_response:
            # Skip deleted properties
            if prop.property_type == 1:  # 1 = PROPERTY_TYPE_ORDINARY (active)
                property_id = prop.name.split("/")[-1]
                display_name = prop.display_name or f"Unnamed Property ({property_id})"
                properties.append((display_name, property_id))
    
    return properties
