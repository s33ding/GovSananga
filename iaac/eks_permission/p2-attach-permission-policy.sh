aws iam attach-role-policy \
  --role-name eks-govsananga-role \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite

aws iam attach-role-policy \
  --role-name eks-govsananga-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

aws iam attach-role-policy \
  --role-name eks-govsananga-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

