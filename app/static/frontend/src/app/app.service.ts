import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse, HttpEventType } from '@angular/common/http';
import { environment } from './../environments/environment';

import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

import { DataProvider } from './dataProvider';
import { Portfolio } from './portfolio';
import { TemperatureScoreSettings } from './temperatureScoreSettings';
import { Alert } from './alert';


@Injectable({ providedIn: 'root' })
export class AppService {

    httpOptions = {
        headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };
    alertHandler: (alert: Alert) => void;

    constructor(private http: HttpClient) { }

    addAlert(alert: Alert) {
        console.log(alert);
    }

    setAlertHandler(addAlert: (alert: Alert) => void) {
        this.addAlert = addAlert;
    }

    /** GET a list of available data providers */
    public getDataProviders(): Observable<DataProvider[]> {
        return this.http.get<DataProvider[]>(`${environment.host}/data_providers`)
            .pipe(
                tap(_ => console.log('fetched data providers')),
                catchError(this.handleError<DataProvider[]>('getDataProviders', []))
            );
    }

    public doParsePortfolio(data: FormData): Observable<Portfolio> {
        return this.http.post<Portfolio>(`${environment.host}/parse_portfolio/`, data)
            .pipe(
                tap(_ => console.log('Parsed portfolio')),
                catchError(this.handleError<Portfolio>('doParsePortfolio', {"portfolio": []}))
            );
    }

    public getTemperatureScore(data: TemperatureScoreSettings): Observable<any> {
        return this.http.post(`${environment.host}/temperature_score/`, data)
            .pipe(
                tap(_ => console.log('Calculated temperature score')),
                catchError(this.handleError<any>('getTemperatureScore', {"aggregated_scores": {}, "companies": []}))
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
