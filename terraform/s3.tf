resource "aws_s3_bucket" "traffic_datalake" {
  bucket = "traffic-violations-datalake"

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_versioning" "traffic_datalake_versioning" {
  bucket = aws_s3_bucket.traffic_datalake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_policy" "traffic_datalake_policy" {
  bucket = aws_s3_bucket.traffic_datalake.id
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::traffic-violations-datalake/*"
    }
  ]
}
POLICY
}