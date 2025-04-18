resource "aws_s3_bucket" "example" {
  bucket = "swap-etl-wbtc"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}