import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse, HttpEventType } from '@angular/common/http';
import { map } from  'rxjs/operators';

import { Observable, of } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';

import { DataProvider } from './dataProvider';


@Injectable({ providedIn: 'root' })
export class AppService {

    httpOptions = {
        headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };

    constructor(private http: HttpClient) { }

    /** GET a list of available data providers */
    getDataProviders(): Observable<DataProvider[]> {
        return this.http.get<DataProvider[]>("http://localhost:5000/data_providers")
            .pipe(
                tap(_ => console.log('fetched data providers')),
                catchError(this.handleError<DataProvider[]>('getDataProviders', []))
            );
    }

    public upload(data): Observable<any> {
        return this.http.post<any>("http://localhost:5000/import_portfolio/", data).pipe(map((event) => {
            console.log(event);

            switch (event.type) {

                case HttpEventType.UploadProgress:
                    const progress = Math.round(100 * event.loaded / event.total);
                    return { status: 'progress', message: progress };

                case HttpEventType.Response:
                    return event.body;
                default:
                    return `Unhandled event: ${event.type}`;
            }
        })
        );
    }

    /** PUT: update the hero on the server */
    //   updateHero(hero: Hero): Observable<any> {
    //     return this.http.put(this.heroesUrl, hero, this.httpOptions).pipe(
    //       tap(_ => this.log(`updated hero id=${hero.id}`)),
    //       catchError(this.handleError<any>('updateHero'))
    //     );
    //   }

    /**
     * Handle Http operation that failed.
     * Let the app continue.
     * @param operation - name of the operation that failed
     * @param result - optional value to return as the observable result
     */
    private handleError<T>(operation = 'operation', result?: T) {
        return (error: any): Observable<T> => {

            // TODO: send the error to remote logging infrastructure
            console.error(error); // log to console instead

            // TODO: better job of transforming error for user consumption
            console.log(`${operation} failed: ${error.message}`);

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }
}


/*
Copyright Google LLC. All Rights Reserved.
Use of this source code is governed by an MIT-style license that
can be found in the LICENSE file at http://angular.io/license
*/