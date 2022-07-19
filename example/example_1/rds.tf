# Create a RDS database for testing 

resource "aws_db_instance" "default" {
  engine         = "postgres"
  engine_version = "11"
  identifier     = "test-db"

  instance_class = "db.t3.micro"
  name           = "testdb"
  username       = "foo"
  password       = "hellohello"

  allocated_storage = 10

  skip_final_snapshot = true
}