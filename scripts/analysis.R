library(ggplot2)

# These paths are relative to the project root where Binder launches.
# This ensures it works whether run from the 'root' or from inside 'scripts/'
if (file.exists("results/foci_counts.csv")) {
  # We are in the Root
  input_path  <- "results/foci_counts.csv"
  output_path <- "results/Validation_Plot_Final.png"
} else if (file.exists("../results/foci_counts.csv")) {
  # We are in the scripts/ folder, so we go up one level
  input_path  <- "../results/foci_counts.csv"
  output_path <- "../results/Validation_Plot_Final.png"
} else {
  stop(paste("Error: CSV not found. Current Dir:", getwd()))
}
df <- read.csv(input_path)

# Ensure numeric types
df$actual   <- as.numeric(df$actual)
df$detected <- as.numeric(df$detected)

# Calculate Statistics
stats <- cor.test(df$actual, df$detected)

# Format r (omit leading zero per APA style: e.g., .88)
r_value <- sub("0", "", round(stats$estimate, 2))

# Format p-value (threshold at .001)
p_raw <- stats$p.value
p_value <- if(p_raw < .001) {
  "< .001"
} else {
  paste0("= ", sub("0", "", format.pval(p_raw, digits = 2)))
}

# Mean Absolute Error Calculation
mae <- round(mean(abs(df$actual - df$detected)), 2)

# Generate Validation Plot
p <- ggplot(df, aes(x = actual, y = detected)) +
  # 1:1 Reference line (Ideal accuracy)
  geom_abline(intercept = 0, slope = 1, linetype = 'dashed', color = 'red', linewidth = 0.8) +

  # Jittered data points to prevent overlap (overplotting)
  geom_jitter(width = 0.1, height = 0.1, color = "#2c3e50", alpha = 0.5, size = 2.5) +

  # Linear Regression trend line
  geom_smooth(method = "lm", formula = y ~ x, color = "#3498db", fill = "#3498db", alpha = 0.1) +

  # Scientific Formatting
  labs(
    title = "Validation of Automated Foci Counting Pipeline",
    subtitle = paste0("Pearson's r = ", r_value, " | p ", p_value, " | MAE = ", mae, " foci"),
    x = "Ground Truth (Manual Count)",
    y = "Algorithm (Watershed Detected)",
    caption = "Red dashed: 1:1 Ideal | Blue: Linear Regression Trend"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(face = "bold", size = 16),
    panel.grid.minor = element_blank(),
    axis.title = element_text(face = "bold")
  )

# Save the Output
# DPI set to 300 for publication quality
ggsave(output_path, p, width = 8, height = 6, dpi = 300)

# Console Summary
cat("\n===========================================")
cat("\n   PIPELINE PERFORMANCE SUMMARY")
cat("\n===========================================")
cat("\nCorrelation (r): ", r_value)
cat("\np-value:        ", p_value)
cat("\nMean Abs Error:  ", mae, "foci")
cat("\nOutput saved:   ", output_path)
cat("\n===========================================\n")