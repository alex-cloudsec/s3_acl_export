import boto3
import pandas as pd
from tqdm import tqdm


def get_s3_buckets_acl():
    s3 = boto3.client('s3')
    buckets_response = s3.list_buckets()

    buckets_data = []

    permission_map = {
        'FULL_CONTROL': 'Full control',
        'WRITE': 'Write',
        'WRITE_ACP': 'Write ACL',
        'READ': 'Read',
        'READ_ACP': 'Read ACL'
    }

    grantee_map = {
        'http://acs.amazonaws.com/groups/global/AllUsers': 'Everyone (public access)',
        'http://acs.amazonaws.com/groups/global/AuthenticatedUsers': 'Authenticated users group (anyone with an AWS account)',
        'http://acs.amazonaws.com/groups/s3/LogDelivery': 'S3 log delivery group'
    }

    for bucket in tqdm(buckets_response['Buckets'], desc='Scanning Buckets', unit='bucket'):
        bucket_name = bucket['Name']
        acl = s3.get_bucket_acl(Bucket=bucket_name)

        for grant in acl['Grants']:
            permission = permission_map.get(grant['Permission'], grant['Permission'])
            grantee_type = grant['Grantee']['Type']

            if grantee_type == 'CanonicalUser':
                grantee = 'Bucket owner (your AWS account)'
            else:
                grantee = grantee_map.get(grant['Grantee'].get('URI', ''), grant['Grantee'].get('ID', ''))

            buckets_data.append({
                'Bucket Name': bucket_name,
                'Permission': permission,
                'Grantee Type': grantee_type,
                'Grantee': grantee
            })

    return buckets_data


def save_to_excel(buckets_data, filename='s3_buckets_acl.xlsx'):
    df = pd.DataFrame(buckets_data)
    df.to_excel(filename, index=False)
    print(f'Results saved to {filename}')


if __name__ == "__main__":
    print("Starting S3 Buckets ACL Scan...")
    buckets_data = get_s3_buckets_acl()
    save_to_excel(buckets_data)
    print("Scan completed.")
