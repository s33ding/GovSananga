aws iam create-role \
  --role-name eks-govsananga-role \
  --assume-role-policy-document file://trust-policy.json
