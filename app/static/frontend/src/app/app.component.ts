import { Component, OnInit } from '@angular/core';
import { AppService } from './app.service';
import { DataProvider } from './dataProvider';
import { Alert } from './alert';
import levenshtein from 'fast-levenshtein';
import { environment } from 'src/environments/environment';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

const AVAILABLE_GROUPING_COLUMNS: string[] = ['Country', 'Region', 'Industry_lvl1', 'Industry_lvl2', 'Industry_lvl3',  'Industry_lvl4', 'sector'];
const AVAILABLE_COLUMNS: string[] = ['company_id', 'Country', 'Region', 'Industry_lvl1', 'Industry_lvl2', 'Industry_lvl3',  'Industry_lvl4', 'sector', 'GHG_scope1+2', 'GHG_scope3',
'market_cap', 'investment_value', 'company_enterprise_value', 'cash_equivalents', 'company_total_assets',
'Target type', 'Scope', 'Intensity_metric', 'base_year', 'start_year', 'end_year', 'reduction_ambition', 'achieved_reduction'];

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    title = 'SBTi-FI Temperature Scoring';
    excelSkiprows = 0;
    isNavbarCollapsed = true;
    availableTargetColumns: string[] = ['company_id', 'company_name', 'investment_value', 'ISIN'];
    availableTimeFrames: string[] = ['short', 'mid', 'long'];
    availableScopeCategories: string[] = ['s1s2', 's3', 's1s2s3'];
    availableAggregationMethods: string[] = ['WATS', 'TETS', 'MOTS', 'EOTS', 'ECOTS', 'AOTS', 'ROTS'];
    availableColumns: string[] = AVAILABLE_COLUMNS;
    availableGroupingColumns: string[] = AVAILABLE_GROUPING_COLUMNS;
    groupingColumns: string[] = [];
    selectedAggregationMethod = 'WATS';
    availableScenarios: any[] = [{'label':'scenario_1', 'description': 'With current targets, rest of portfolio business as usual'}, {'label':'scenario_2', 'description': 'Scenario 1: "What-if" - all companies set targets (default scores go to 2.0)'}, {'value': {"number": 2}, 'label':'scenario_3', 'description': 'Scenario 2: "What-if" - all companies with targets get SBTs (scores from targets are capped at 1.75)'}, {'value': {"number": 1}, 'label':'scenario_4', 'description': 'Scenario 3a: "What-if" - the 10 highest contributors to the portfolio set targets (scores of 10 highest contributors are capped at 2.0)'}, {'value': {"number": 1}, 'label':'scenario_5', 'description': 'Scenario 3b: "What-if" - the 10 highest contributors to the portfolio set SBTs (scores of 10 highest contributors are capped at 1.75)'}];
    filterTimeFrames: string[] = ['mid'];
    filterScopeCategory: string[] = ['s1s2', 's1s2s3'];
    includeColumns: string[] = [];
    availableDefaultScores: number[] = [3.2, 3.9, 4.5];
    defaultScore = 3.2;
    uploadedFiles: Array<File>;
    selectedScenario: { [key: string]: number } = {'number': 0};
    selectedDumpOption: boolean = false;
    selectedDataProviders: string[] = [];
    selectedDataProviders1 = '';
    selectedDataProvider1Path = '';
    selectedDataProviders2 = '';
    selectedDataProvider2Path = '';
    selectedDataProviderPaths: string[] = [];
    dataProviders: DataProvider[];
    dataProviderFile1: Array<File>;
    dataProviderFile2: Array<File>;
    portfolio: any[] = [];
    columns: string[] = [];
    columnMapping: { [key: string]: string } = {};
    resultTimeFrames: string[] = [];
    resultColumns: string[] = [];
    resultDumpColumns: string[] = [];
    resultGroups: string[] = [];
    resultTargets: any[] = [];
    dataDump:  any[] = [];
    resultItems: any[] = [];
    resultDistribution:  { [key: string]: string } = {};
    resultScores: { [key: string]: number } = {};
    selectedContributions: { [key: string]: number }[] = [];
    alerts: Alert[] = [];
    loading = false;
    coverage: number;

    constructor(private appService: AppService, private modalService: NgbModal) { }

    /**
     * Initialize the app.
     */
    ngOnInit() {
        this.appService.setAlertHandler(this.addAlert.bind(this));
        this.getDataProviders();
    }

    /**
     * Adds alert
     */
    addAlert(alert: Alert) {
        this.alerts.push(alert);
    }

    /**
     * Closes alert
     */
    closeAlert(alert: Alert) {
        this.alerts.splice(this.alerts.indexOf(alert), 1);
    }

    /**
     * Update the uploaded files.
     */
    onFileChange(element) {
        this.uploadedFiles = element.target.files;
    }
    onFileChangeDataProvider1(element) {
        this.dataProviderFile1 = element.target.files;
    }
    onFileChangeDataProvider2(element) {
        this.dataProviderFile2 = element.target.files;
    }


    /**
     * Select Scenario
     */
    addScenario(element) {
      const dicts = {'scenario_1': {'number': 0}, 'scenario_2': {'number': 1}, 'scenario_3': {'number': 2}, 'scenario_4': {'number': 3, 'engagement_type': 'set_targets'}, 'scenario_5': {'number': 3, 'engagement_type': 'set_SBTi_targets'}};
      this.selectedScenario = dicts[element.target.value];
    }

    /**
     * Select Data Dump option
     */
    addDumpOption(element) {
        const dump = {"false": false, "true": true}
      this.selectedDumpOption = dump[element.target.value];
    }


    openContributors(group: string, timeFrame: string, item: string, template) {
        console.log('contributions to group \'' + group + '\' and timeFrame \'' + timeFrame + '\' and item \'' + item + '\'.');
        this.selectedContributions = this.resultScores[timeFrame][group][item].contributions;
        this.modalService.open(template, { scrollable: true, size: 'xl' });
    }

    /**
     * Gets data providers
     */
    getDataProviders(): void {
        this.appService.getDataProviders()
            .subscribe(dataProviders => this.dataProviders = dataProviders);
    }

    /**
     * Updates grouping columns
     */
    updateAvailableColumns(): void {
        this.availableGroupingColumns = AVAILABLE_GROUPING_COLUMNS;
        this.availableGroupingColumns = this.availableGroupingColumns
          .concat(this.columns.filter((column) => this.columnMapping[column] === null));
        this.availableColumns = AVAILABLE_COLUMNS;
        this.availableColumns = this.availableColumns.concat(this.columns.filter((column) => this.columnMapping[column] === null));
    }

    /**
     * Export some data (formatted as a 2d array) as a CSV file.
     */
    exportToCsv(filename: string, rows: Array<Array<any>>) {
        const processRow = row => {
            let finalVal = '';
            for (let j = 0; j < row.length; j++) {
                let innerValue = row[j] === null ? '' : row[j].toString();
                if (row[j] instanceof Date) {
                    innerValue = row[j].toLocaleString();
                }
                let result = innerValue.replace(/"/g, '""');
                if (result.search(/("|,|\n)/g) >= 0) {
                    result = '"' + result + '"';
                }
                if (j > 0) {
                    finalVal += ',';
                }
                finalVal += result;
            }
            return finalVal + '\n';
        };

        let csvFile = '';
        for (const row of rows) {
          csvFile += processRow(row);
        }

        const blob = new Blob([csvFile], { type: 'text/csv;charset=utf-8;' });
        if (navigator.msSaveBlob) { // IE 10+
            navigator.msSaveBlob(blob, filename);
        } else {
            const link = document.createElement('a');
            if (link.download !== undefined) { // feature detection
                // Browsers that support HTML5 download attribute
                const url = URL.createObjectURL(blob);
                link.setAttribute('href', url);
                link.setAttribute('download', filename);
                link.style.visibility = 'hidden';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        }
    }

    /**
     * Parses excel file by creating an API request.
     */
    parseExcel() {
        const formData = new FormData();
        formData.append('file', this.uploadedFiles[0], this.uploadedFiles[0].name);
        formData.append('skiprows', this.excelSkiprows.toString());
        const that = this;
        const assigned = [];
        this.loading = true;

        this.appService.doParsePortfolio(formData).subscribe((response) => {
            this.loading = false;
            this.portfolio = response.portfolio;
            if (this.portfolio.length > 0) {
                this.columns = Object.keys(this.portfolio[0]);
                this.columnMapping = this.columns.reduce((map, obj) => {
                    map[obj] = null;
                    // We use the Levenshtein distance to try and map the columns to the targets
                    const sortedMappings = that.availableTargetColumns.filter(elem => !(elem in assigned)).sort((a, b) => {
                        return levenshtein.get(a, obj) - levenshtein.get(b, obj);
                    });
                    if (sortedMappings.length > 0 &&
                        levenshtein.get(sortedMappings[0], obj) < environment.levenshteinThreshold){
                        // If it's smaller than the threshold, we'll assign this column
                        map[obj] = sortedMappings[0];
                        assigned.push(sortedMappings[0]);
                    }
                    return map;
                }, {});
                this.updateAvailableColumns();
            }
        });
    }

    /**
     * Accordion
     */
    toggleAccordion(elementDiv) {
      const x = document.getElementById(elementDiv);
      if (x.style.display === 'none') {
        x.style.display = 'block';
      } else {
        x.style.display = 'none';
      }
    }

    /**
     * Exports csv
     */
    exportCSV() {
        const csv = this.resultTargets.map(row => Object.values(row));
        csv.unshift(this.resultColumns);
        this.exportToCsv('temperature_scores.csv', csv);
    }
    /**
     * Data dump csv
     */
    dumpCSV() {
        const dump = this.dataDump.map(row => Object.values(row));
        dump.unshift(this.resultDumpColumns);
        this.exportToCsv('data_dump.csv', dump);
    }


    /**
     * Gets the temperature score
     */
    getTemperatureScore(f) {
        this.loading = true;
        const columnsMapped = Object.keys(this.columnMapping).filter((key) => this.columnMapping[key] !== null);
        const columnsUnmapped = Object.keys(this.columnMapping).filter((key) => this.columnMapping[key] === null);
        const portfolioData = this.portfolio.map((obj) => {
            const newObj = {};
            for (const column of columnsMapped) {
                newObj[this.columnMapping[column]] = obj[column];
            }
            for (const column of columnsUnmapped) {
                newObj[column] = obj[column];
            }
            return newObj;
        });

        this.selectedDataProviders = [this.selectedDataProviders1, this.selectedDataProviders2];
        this.selectedDataProviderPaths = [this.selectedDataProvider1Path, this.selectedDataProvider2Path];

        const formData1 = new FormData();
        if (this.dataProviderFile1) {
            formData1.append('file', this.dataProviderFile1[0], this.dataProviderFile1[0].name);
        }
        const formData2 = new FormData();
        if (this.dataProviderFile2) {
            formData2.append('file', this.dataProviderFile2[0], this.dataProviderFile2[0].name);
        }

        this.appService.getTemperatureScore({
            aggregation_method: this.selectedAggregationMethod,
            data_providers: [],
            filter_scope_category: this.filterScopeCategory,
            filter_time_frame: this.filterTimeFrames,
            include_columns: this.includeColumns,
            grouping_columns: this.groupingColumns,
            default_score: this.defaultScore,
            companies: portfolioData,
            scenario: this.selectedScenario,
            anonymize_data_dump: this.selectedDumpOption
        })
            .subscribe((response) => {
                this.loading = false;
                if (response !== undefined) {

                    console.log(response);
                    this.resultScores = response.aggregated_scores;
                    this.resultTargets = response.companies;
                    this.dataDump = response.scores;
                    this.coverage = response.coverage;
                    this.resultTimeFrames = Object.keys(response.aggregated_scores);
                    const firstTimeFrame = this.resultTimeFrames[0];
                    this.resultGroups = Object.keys(response.aggregated_scores[firstTimeFrame]);
                    this.resultItems = Object.keys(response.aggregated_scores[firstTimeFrame][this.resultGroups[0]]);
                    this.resultDistribution = response["feature_distribution"];
                    if (this.resultTargets.length > 0) {
                        this.resultColumns = Object.keys(this.resultTargets[0]);
                    }
                    if (this.dataDump.length > 0) {
                        this.resultDumpColumns = Object.keys(this.dataDump[0]);
                    }
                }
            });
    }
}
