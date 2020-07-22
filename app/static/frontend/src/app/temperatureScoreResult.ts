export interface TemperatureScoreResult {
  aggregated_scores: { [key: string]: number };
  coverage: number;
  companies: any[];
  scores:  any[];
}
