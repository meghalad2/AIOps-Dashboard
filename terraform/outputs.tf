output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS Control Plane"
  value       = aws_eks_cluster.main.endpoint
}

output "eks_cluster_name" {
  description = "EKS Cluster Name"
  value       = aws_eks_cluster.main.name
}

output "jenkins_public_ip" {
  description = "Public IP address of the Jenkins Build Server"
  value       = aws_instance.jenkins.public_ip
}
