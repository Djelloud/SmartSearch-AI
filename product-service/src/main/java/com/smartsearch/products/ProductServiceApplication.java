package com.smartsearch.products;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;

@SpringBootApplication
@RestController
@CrossOrigin(origins = "*")
public class ProductServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(ProductServiceApplication.class, args);
	}

	@GetMapping("/")
	public String home() {
		return "Product Catalog Service is running!";
	}

	@GetMapping("/health")
	public HealthResponse health() {
		return new HealthResponse("healthy", "Product Service v1.0");
	}

	record HealthResponse(String status, String service) {}
}