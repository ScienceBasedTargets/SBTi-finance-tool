import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from './../environments/environment';

import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

import { DataProvider } from './dataProvider';
import { Portfolio } from './portfolio';
import { TemperatureScoreSettings } from './temperatureScoreSettings';
import { Alert } from './alert';
import { TemperatureScoreResult } from './temperatureScoreResult';


@Injectable({ providedIn: 'root' })
export class AppService {

    httpOptions = {
        headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };

    constructor(private http: HttpClient) { }

    /**
     * Adds alert to the log. This can be overwritten by setting the alert handler.
     * @param alert 
     */
    protected addAlert(alert: Alert) {
        console.log(alert);
    }

    /**
     * Sets the alert handler.
     * @param addAlert A method that takes an Alert object as parameter.
     */
    public setAlertHandler(addAlert: (alert: Alert) => void) {
        this.addAlert = addAlert;
    }

    /**
     * Gets a list of the available data providers
     * @returns data providers 
     */
    public getDataProviders(): Observable<DataProvider[]> {
        return this.http.get<DataProvider[]>(`${environment.host}/data_providers`)
            .pipe(
                tap(_ => console.log('fetched data providers')),
                catchError(this.handleError<DataProvider[]>('getDataProviders', []))
            );
    }

    /**
     * Parse an Excel portfolio file.
     * @param data 
     * @returns parse portfolio 
     */
    public doParsePortfolio(data: FormData): Observable<Portfolio> {
        return this.http.post<Portfolio>(`${environment.host}/parse_portfolio/`, data)
            .pipe(
                tap(_ => console.log('Parsed portfolio')),
                catchError(this.handleError<Portfolio>('doParsePortfolio', {"portfolio": []}))
            );
    }

    /**
     * Calculate the temperature score
     * @param data 
     * @returns temperature score 
     */
    public getTemperatureScore(data: TemperatureScoreSettings): Observable<TemperatureScoreResult> {
        return this.http.post<TemperatureScoreResult>(`${environment.host}/temperature_score/`, data)
            .pipe(
                tap(_ => console.log('Calculated temperature score')),
                catchError(this.handleError<TemperatureScoreResult>('getTemperatureScore', {"aggregated_scores": {}, "coverage": 0.00, "companies": []}))
            );
    }

    /**
     * Handle Http operation that failed.
     * Let the app continue.
     * @param operation - name of the operation that failed
     * @param result - optional value to return as the observable result
     */
    private handleError<T>(operation = 'operation', result?: T) {
        return (error: any): Observable<T> => {

            if (error.status === 500) {
                this.addAlert({type: "warning", message: "There was a technical error. Please check your inputs."});
            } else {
                this.addAlert({type: "danger", message: "Nn unknown error occured."});
                console.error(error); // log to console instead
            }

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }
}
