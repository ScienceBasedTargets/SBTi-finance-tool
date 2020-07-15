export interface TemperatureScoreSettings {
    aggregation_method: string;
    data_providers: Object[];
    filter_scope_category: string[];
    filter_time_frame: string[];
    include_columns: string[];
    grouping_columns: string[];
    default_score: number;
    companies: Object[];
}
