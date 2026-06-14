variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "cluster_name" {
  description = "Name of the EKS Cluster"
  type        = string
  default     = "self-healing-cluster"
}

variable "jenkins_instance_type" {
  description = "EC2 Instance type for Jenkins Server"
  type        = string
  default     = "t3.large"
}

variable "key_name" {
  description = "Name of the AWS SSH key pair"
  type        = string
  default     = "devops-key"
}
