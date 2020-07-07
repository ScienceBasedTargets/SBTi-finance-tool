import { Component, OnInit } from '@angular/core';
import { AppService } from './app.service';
import { DataProvider } from './dataProvider';
import { Alert } from './alert';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
    title = 'frontend';
    excelSkiprows = 0;
    isNavbarCollapsed = true;
    availableTargetColumns: string[] = ["company_id", "company_name", "portfolio_weight", "investment_value"];
    availableTimeFrames: string[] = ["short", "mid", "long"];
    availableScopeCategories: string[] = ["s1s2", "s3", "s1s2s3"];
    availableAggregationMethods: string[] = ["WATS", "TETS", "MOTS", "EOTS", "ECOTS", "AOTS"];
    availableColumns: string[] = ["company_id", "industry", "s1s2_emissions", "s3_emissions", "portfolio_weight",
        "market_cap", "investment_value", "company_enterprise_value", "company_ev_plus_cash", "company_total_assets",
        "target_reference_number", "scope", "base_year", "start_year", "target_year", "reduction_from_base_year",
        "emissions_in_scope", "achieved_reduction"];
    selectedAggregationMethod: string = null;
    filterTimeFrames: string[] = [];
    filterScopeCategory: string[] = [];
    includeColumns: string[] = [];
    selectedDataProviders: string[] = [];
    defaultScore: number = 3.2;
    uploadedFiles: Array<File>;
    dataProviders: DataProvider[];
    portfolio: Object[] = [];
    columns: string[] = [];
    columnMapping: { [key: string]: string } = {};
    resultColumns: string[] = [];
    resultTargets: Object[] = [];
    resultScores: { [key: string]: number } = {};
    alerts: Alert[] = [];


    constructor(private appService: AppService) { }

    ngOnInit() {
        this.appService.setAlertHandler(this.addAlert.bind(this))
        this.getDataProviders();
    }

    addAlert(alert: Alert) {
        this.alerts.push(alert);
    }

    close(alert: Alert) {
        this.alerts.splice(this.alerts.indexOf(alert), 1);
    }

    fileChange(element) {
        this.uploadedFiles = element.target.files;
    }

    getDataProviders(): void {
        this.appService.getDataProviders()
            .subscribe(dataProviders => this.dataProviders = dataProviders);
    }

    exportToCsv(filename: string, rows: Array<Array<any>>) {
        /**
         * Export some data (formatted as a 2d array) as a CSV file.
         * @param filename 
         * @param row 
         */
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

    parseExcel() {
        let formData = new FormData();
        formData.append("file", this.uploadedFiles[0], this.uploadedFiles[0].name);
        formData.append("skiprows", this.excelSkiprows.toString());

        this.appService.doParsePortfolio(formData).subscribe((response) => {
            this.portfolio = response["portfolio"];
            if (this.portfolio.length > 0) {
                this.columns = Object.keys(this.portfolio[0]);
                this.columnMapping = this.columns.reduce(function (map, obj) {
                    map[obj] = null;
                    return map;
                }, {});
            }
        })
    }

    exportCSV() {
        let csv = this.resultTargets.map(row => Object.values(row));
        csv.unshift(this.resultColumns);
        this.exportToCsv("temperature_scores.csv", csv);
    }

    onSubmit(f) {
        let columnsToUse = Object.keys(this.columnMapping).filter((key) => this.columnMapping[key] !== null);
        let portfolioData = this.portfolio.map((obj) => {
            let newObj = {};
            for (let column of columnsToUse) {
                newObj[this.columnMapping[column]] = obj[column];
            }
            return newObj;
        });
        this.appService.getTemperatureScore({
            "aggregation_method": this.selectedAggregationMethod,
            "data_providers": this.selectedDataProviders,
            "filter_scope_category": this.filterScopeCategory,
            "filter_time_frame": this.filterTimeFrames,
            "include_columns": this.includeColumns,
            "default_score": this.defaultScore,
            "companies": portfolioData,
        })
            .subscribe((response) => {
                if (response !== undefined) { 
                    this.resultScores = response["aggregated_scores"];
                    this.resultTargets = response["companies"];
                    if (this.resultTargets.length > 0) {
                        this.resultColumns = Object.keys(this.resultTargets[0]);
                    }
                }
            })
    }
}
