resource "aws_db_instance" "dw" {
  identifier             = "dw"
  engine                 = "postgres"
  engine_version         = "15.3"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_encrypted      = true
  publicly_accessible    = true
  skip_final_snapshot    = true
  username              = var.db_username
  password              = var.db_password
}

resource "aws_security_group" "traffic_rds_sg" {
  name        = "traffic-rds-sg"
  description = "Allow inbound PostgreSQL access"
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}