import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {AppThunkAction} from "src/redux/store";

import {timeout} from "src/util";
import {API_RETRY_TIMEOUT, ApiError, ApiErrorModel} from "src/api/base";

import {ApiReportModel, ApiReportStatus, ReportApi} from "src/api/report";
import {UserController} from "src/redux/user";

export interface ReportState {
    reports: Report[]
    currentReport: number
    newReportStatus: NewReportStatus
}

export interface Report {
    id: number
    title: string
    status: ReportStatus
    params: ReportParam[]
    statuses: ReportDetailedStatuses
    createdAt: number
    texts: ReportText[]
}

export interface ReportText {
    text: string
    active: boolean
    version: number
}

export interface ReportDetailedStatuses {
    OD: ReportStatus,
    AV: ReportStatus,
    MAC: ReportStatus,
    LLM: ReportStatus,
    PERIPHERAL: ReportStatus,
    OTHER: ReportStatus,
}

export enum ReportStatus {
    PENDING = "pending",
    LOCALIZATION = "localization",
    CLASSIFICATION = "classification",
    READ = "read",
    GENERATION = "generation",
    UPDATING = "updating"
}

export interface ReportParam {
    name: string
    type: "boolean" | "enum" | "string"
    data: ReportParamData
}

export interface ReportParamData {
    value: boolean | string
    variants?: string[]
}

export enum NewReportStatus {
    EMPTY,
    UPLOAD,
    FAILED,
}

export enum ReportImageType {
    SOURCE = "source",
    OD_CONTOUR = "od_contour",
    MAC_CONTOUR = "mac_contour",
    AV_SEGMENTATION = "av_segmentation",
}

function mapApiReportModel(report: ApiReportModel): Report {
    return {
        id: report.id,
        title: report.title,
        status: mapApiReportStatus(report.status),
        params: report.params?.map(param => ({
            name: param.name,
            type: param.type,
            data: {
                variants: param.data.variants,
                value: param.data.value
            }
        })),
        statuses: {
            OD: mapApiReportStatus(report.statuses?.OD),
            AV: mapApiReportStatus(report.statuses?.AV),
            MAC: mapApiReportStatus(report.statuses?.MAC),
            LLM: mapApiReportStatus(report.statuses?.LLM),
            PERIPHERAL: ReportStatus.CLASSIFICATION,
            OTHER: ReportStatus.CLASSIFICATION,
        },
        createdAt: report.created_at,
        texts: report.texts?.map(text => ({
            text: text.text,
            active: text.active,
            version: text.version
        }))
    }
}

function mapApiReportStatus(status: ApiReportStatus): ReportStatus {
    return status as unknown as ReportStatus // TODO: fix
}

interface UpdatePayload {
    id: number
    report: Report
}

interface UpdateParamPayload {
    id: number
    paramName: string
    paramValue: boolean | string
}

interface UpdateTextPayload {
    id: number
    text: string
}

const reportSlice = createSlice({
    name: "report",
    initialState: <ReportState>{
        reports: null,
        currentReport: -1,
        newReportStatus: NewReportStatus.EMPTY,
    },
    reducers: {
        reset(state, action: PayloadAction<number>) {
            state.reports = null
            state.currentReport = null
            state.newReportStatus = NewReportStatus.EMPTY
        },

        resetCurrent(state) {
            state.currentReport = null
        },

        updateCurrent(state, action: PayloadAction<number>) {
            state.currentReport = action.payload
        },

        setReports(state, action: PayloadAction<Report[]>) {
            state.reports = action.payload
        },

        setNewReportStatus(state, action: PayloadAction<NewReportStatus>) {
            state.newReportStatus = action.payload
        },

        addReport(state, action: PayloadAction<Report>) {
            // Prevent report duplicates
            if (state.reports.find(report => report.id == action.payload.id)) {
                return
            }

            state.reports = state.reports.concat([action.payload])
        },

        updateReport(state, action: PayloadAction<UpdatePayload>) {
            state.reports = state.reports.map(report => {
                if (report.id != action.payload.id) {
                    return report
                }

                return action.payload.report
            })
        },

        updateReportParam(state, action: PayloadAction<UpdateParamPayload>) {
            state.reports = state.reports.map(report => {
                if (report.id != action.payload.id) {
                    return report
                }

                report.params = report.params.map(param => {
                    if (param.name == action.payload.paramName) {
                        return {
                            type: param.type,
                            name: param.name,
                            data: {
                                variants: param.data.variants,
                                value: action.payload.paramValue
                            }
                        }
                    }

                    return param
                })

                return report
            })
        },

        deleteReport(state, action: PayloadAction<number>) {
            state.reports = state.reports.filter(report => report.id != action.payload)

            // Drop current report if it's deleted
            if (state.currentReport == action.payload) {
                state.currentReport = null
            }
        },

        // rephraseReport(state, action: PayloadAction<number>) {
        //     state.reports = state.reports.map(report => {
        //         if (report.id != action.payload.id) {
        //             return report
        //         }

        //         report.params = report.params.map(param => {
        //             if (param.name == action.payload.paramName) {
        //                 return {
        //                     type: param.type,
        //                     name: param.name,
        //                     data: {
        //                         variants: param.data.variants,
        //                         value: action.payload.paramValue
        //                     }
        //                 }
        //             }

        //             return param
        //         })

        //         return report
        //     })
        // }
    }
})

export const ReportActions = reportSlice.actions

export const reportReducer = reportSlice.reducer


export class ReportController {
    static create(file: File): AppThunkAction {
        return async function (dispatch) {
            dispatch(ReportActions.setNewReportStatus(NewReportStatus.UPLOAD))

            try {
                let fileContent = await encodeFileToBase64(file)
                let report = await ReportApi.create(file.name, fileContent)

                dispatch(ReportActions.setNewReportStatus(NewReportStatus.EMPTY))
                dispatch(ReportActions.addReport(mapApiReportModel(report)))
                dispatch(ReportActions.updateCurrent(report.id))
            } catch (e) {
                let apiError = e as ApiErrorModel

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout())
                        return
                }

                dispatch(ReportActions.setNewReportStatus(NewReportStatus.FAILED))
            }
        }
    }

    static get(id: number): AppThunkAction {
        return async function (dispatch) {
            try {
                let report = await ReportApi.get(id)
                dispatch(ReportActions.updateReport({id, report: mapApiReportModel(report)}))
            } catch (e) {
                let apiError = e as ApiErrorModel

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout())
                        return
                }

                await timeout(API_RETRY_TIMEOUT)
                dispatch(ReportController.get(id))
            }
        }
    }

    static getImageUrl(id: number, imageType: ReportImageType): string {
        return ReportApi.getImageUrl(id, imageType)
    }

    static list(): AppThunkAction {
        return async function (dispatch) {
            try {
                let reports = await ReportApi.list()
                dispatch(ReportActions.setReports(reports.map(mapApiReportModel)))
            } catch (e) {
                let apiError = e as ApiErrorModel

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout())
                        return
                }

                await timeout(API_RETRY_TIMEOUT)
                dispatch(ReportController.list())
            }
        }
    }

    
    static update(report: Report): AppThunkAction<Promise<void>> {
        return async function (dispatch) {
            try {
                await ReportApi.update(
                    report.id,
                    report.title,
                    report.params.map(param => ({
                        type: param.type,
                        name: param.name,
                        data: {
                            variants: param.data.variants,
                            value: param.data.value,
                        }
                    }))
                );
                // Возвращаем Promise, резолвнутый значением undefined
                return;
            } catch (e) {
                let apiError = e as ApiErrorModel;

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout());
                        return;
                }

                await timeout(API_RETRY_TIMEOUT);
                return dispatch(ReportController.update(report));
            }
        }
    }


    // static update(report: Report): AppThunkAction {
    //     return async function (dispatch) {
    //         try {
    //             await ReportApi.update(
    //                 report.id,
    //                 report.title,
    //                 report.params.map(param => {
    //                     return {
    //                         type: param.type,
    //                         name: param.name,
    //                         data: {
    //                             variants: param.data.variants,
    //                             value: param.data.value,
    //                         }
    //                     }
    //                 })
    //             )
    //         } catch (e) {
    //             let apiError = e as ApiErrorModel

    //             switch (apiError.detail) {
    //                 case ApiError.UNAUTHORIZED:
    //                     dispatch(UserController.logout())
    //                     return
    //             }

    //             await timeout(API_RETRY_TIMEOUT)
    //             dispatch(ReportController.update(report))
    //         }
    //     }
    // }

    static delete(id: number): AppThunkAction {
        return async function (dispatch) {
            try {
                await ReportApi.delete(id)
                dispatch(ReportActions.deleteReport(id))
            } catch (e) {
                let apiError = e as ApiErrorModel

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout())
                        return
                }

                await timeout(API_RETRY_TIMEOUT)
                dispatch(ReportController.delete(id))
            }
        }
    }

    static rephrase(id: number): AppThunkAction<Promise<void>> {
        return async function (dispatch) {
            try {
                await ReportApi.rephrase(id)
                
                return;
            } catch (e) {
                let apiError = e as ApiErrorModel

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout())
                        return
                }

                await timeout(API_RETRY_TIMEOUT)
                dispatch(ReportController.rephrase(id))
            }
        }
    }

    static update_active(id: number, version: number): AppThunkAction<Promise<void>> {
        return async function (dispatch) {
            try {
                await ReportApi.update_active(id, version)
                
                return;
            } catch (e) {
                let apiError = e as ApiErrorModel

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout())
                        return
                }

                await timeout(API_RETRY_TIMEOUT)
                dispatch(ReportController.update_active(id, version))
            }
        }
    }

    static create_pdf(id: number): AppThunkAction<Promise<void>> {
        return async function (dispatch) {
            try {
                const blob = await ReportApi.create_pdf(id);
            
                // Создание ссылки для скачивания
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `report_${id}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
            } catch (e) {
                let apiError = e as ApiErrorModel

                switch (apiError.detail) {
                    case ApiError.UNAUTHORIZED:
                        dispatch(UserController.logout())
                        return
                }

                await timeout(API_RETRY_TIMEOUT)
                dispatch(ReportController.create_pdf(id))
            }
        }
    }
}

async function encodeFileToBase64(file: File): Promise<string> {
    return new Promise<string>((resolve, reject) => {
        let reader = new FileReader()

        reader.onload = () => {
            let str = reader.result as string
            if (str == null) {
                reject()
                return
            }

            resolve(str.split(",").pop())
        }
        reader.onerror = () => reject()

        reader.readAsDataURL(file)
    })
}
