export interface TemperatureScoreSettings {
  aggregation_method: string;
  data_providers: any[];
  filter_scope_category: string[];
  filter_time_frame: string[];
  include_columns: string[];
  grouping_columns: string[];
  default_score: number;
  companies: any[];
  scenario: { [key: string]: number };
  data_dump: { [key: string]: boolean };
}
