import { Component, OnInit } from '@angular/core';
import { AppService } from './app.service';
import { DataProvider } from './dataProvider';
import { Alert } from './alert';
import levenshtein from 'fast-levenshtein';
import { environment } from 'src/environments/environment';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

const AVAILABLE_GROUPING_COLUMNS: string[] = ["industry"];
const AVAILABLE_COLUMNS: string[] = ["company_id", "industry", "s1s2_emissions", "s3_emissions", "portfolio_weight",
"market_cap", "investment_value", "company_enterprise_value", "company_ev_plus_cash", "company_total_assets",
"target_reference_number", "scope", "base_year", "start_year", "target_year", "reduction_from_base_year",
"emissions_in_scope", "achieved_reduction"];

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    title = 'SBTi Temperature score';
    excelSkiprows: number = 0;
    isNavbarCollapsed: boolean = true;
    availableTargetColumns: string[] = ["company_id", "company_name", "portfolio_weight", "investment_value"];
    availableTimeFrames: string[] = ["short", "mid", "long"];
    availableScopeCategories: string[] = ["s1s2", "s3", "s1s2s3"];
    availableAggregationMethods: string[] = ["WATS", "TETS", "MOTS", "EOTS", "ECOTS", "AOTS"];
    availableColumns: string[] = AVAILABLE_COLUMNS;
    availableGroupingColumns: string[] = AVAILABLE_GROUPING_COLUMNS;
    groupingColumns: string[] = [];
    selectedAggregationMethod: string = "WATS";
    filterTimeFrames: string[] = [];
    filterScopeCategory: string[] = [];
    includeColumns: string[] = [];
    selectedDataProviders: string[] = [];
    availableDefaultScores: number[] = [3.2, 3.9, 4.5];
    defaultScore: number = 3.2;
    uploadedFiles: Array<File>;
    dataProviders: DataProvider[];
    portfolio: Object[] = [];
    columns: string[] = [];
    columnMapping: { [key: string]: string } = {};
    resultTimeFrames: string[] = [];
    resultColumns: string[] = [];
    resultGroups: string[] = [];
    resultTargets: Object[] = [];
    resultScores: { [key: string]: number } = {};
    selectedContributions: { [key: string]: number }[] = [];
    alerts: Alert[] = [];
    loading: boolean = false;
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
     * @param alert
     */
    addAlert(alert: Alert) {
        this.alerts.push(alert);
    }

    /**
     * Closes alert
     * @param alert
     */
    closeAlert(alert: Alert) {
        this.alerts.splice(this.alerts.indexOf(alert), 1);
    }

    /**
     * Update the uploaded files.
     * @param element
     */
    onFileChange(element) {
        this.uploadedFiles = element.target.files;
    }

    openContributors(group: string, timeFrame: string, template) {
        console.log(group);
        console.log(timeFrame);
        this.selectedContributions = this.resultScores[timeFrame][group]["contributions"];
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
        this.availableGroupingColumns = this.availableGroupingColumns.concat(this.columns.filter((column) => this.columnMapping[column] === null));
        this.availableColumns = AVAILABLE_COLUMNS;
        this.availableColumns = this.availableColumns.concat(this.columns.filter((column) => this.columnMapping[column] === null));
    }

    /**
         * Export some data (formatted as a 2d array) as a CSV file.
     * @param filename
     * @param rows
     */
    exportToCsv(filename: string, rows: Array<Array<any>>) {
        var processRow = function (row) {
            var finalVal = '';
            for (var j = 0; j < row.length; j++) {
                var innerValue = row[j] === null ? '' : row[j].toString();
                if (row[j] instanceof Date) {
                    innerValue = row[j].toLocaleString();
                };
                var result = innerValue.replace(/"/g, '""');
                if (result.search(/("|,|\n)/g) >= 0)
                    result = '"' + result + '"';
                if (j > 0)
                    finalVal += ',';
                finalVal += result;
            }
            return finalVal + '\n';
        };

        var csvFile = '';
        for (var i = 0; i < rows.length; i++) {
            csvFile += processRow(rows[i]);
        }

        var blob = new Blob([csvFile], { type: 'text/csv;charset=utf-8;' });
        if (navigator.msSaveBlob) { // IE 10+
            navigator.msSaveBlob(blob, filename);
        } else {
            var link = document.createElement("a");
            if (link.download !== undefined) { // feature detection
                // Browsers that support HTML5 download attribute
                var url = URL.createObjectURL(blob);
                link.setAttribute("href", url);
                link.setAttribute("download", filename);
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
        let formData = new FormData();
        formData.append("file", this.uploadedFiles[0], this.uploadedFiles[0].name);
        formData.append("skiprows", this.excelSkiprows.toString());
        const that = this;
        let assigned = [];
        this.loading = true;

        this.appService.doParsePortfolio(formData).subscribe((response) => {
            this.loading = false;
            this.portfolio = response["portfolio"];
            if (this.portfolio.length > 0) {
                this.columns = Object.keys(this.portfolio[0]);
                this.columnMapping = this.columns.reduce(function (map, obj) {
                    map[obj] = null;
                    // We use the Levenshtein distance to try and map the columns to the targets
                    let sortedMappings = that.availableTargetColumns.filter(elem => !(elem in assigned)).sort((a, b) => {
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
        })
    }

    /**
     * Exports csv
     */
    exportCSV() {
        let csv = this.resultTargets.map(row => Object.values(row));
        csv.unshift(this.resultColumns);
        this.exportToCsv("temperature_scores.csv", csv);
    }

    /**
     * Gets the temperature score
     * @param f
     */
    getTemperatureScore(f) {
        this.loading = true;
        let columnsMapped = Object.keys(this.columnMapping).filter((key) => this.columnMapping[key] !== null);
        let columnsUnmapped = Object.keys(this.columnMapping).filter((key) => this.columnMapping[key] === null);
        let portfolioData = this.portfolio.map((obj) => {
            let newObj = {};
            for (let column of columnsMapped) {
                newObj[this.columnMapping[column]] = obj[column];
            }
            for (let column of columnsUnmapped) {
                newObj[column] = obj[column];
            }
            return newObj;
        });
        this.appService.getTemperatureScore({
            "aggregation_method": this.selectedAggregationMethod,
            "data_providers": this.selectedDataProviders,
            "filter_scope_category": this.filterScopeCategory,
            "filter_time_frame": this.filterTimeFrames,
            "include_columns": this.includeColumns,
            "grouping_columns": this.groupingColumns,
            "default_score": this.defaultScore,
            "companies": portfolioData,
        })
            .subscribe((response) => {
                this.loading = false;
                if (response !== undefined) {
                    this.resultScores = response["aggregated_scores"];
                    this.resultTargets = response["companies"];
                    this.coverage = response["coverage"];
                    this.resultTimeFrames = Object.keys(response["aggregated_scores"]);
                    this.resultGroups = Object.keys(response["aggregated_scores"]["short"]);
                    if (this.resultTargets.length > 0) {
                        this.resultColumns = Object.keys(this.resultTargets[0]);
                    }
                }
            })
    }
}
