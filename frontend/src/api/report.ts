import {getAccessToken, HttpMethod, makeHttpRequest} from "src/api/base";

export interface ApiReportModel {
    id: number
    title: string
    status: ApiReportStatus
    params: ApiReportParam[]
    statuses: ApiReportDetailedStatuses
    created_at: number
    texts: ApiReportText[]
}

export interface ApiReportText {
    text: string
    active: boolean
    version: number
}

export interface ApiReportDetailedStatuses {
    OD: ApiReportStatus
    MAC: ApiReportStatus
    AV: ApiReportStatus
    LLM: ApiReportStatus
}

export enum ApiReportStatus {
    PENDING = "pending",
    LOCALIZATION = "localization",
    CLASSIFICATION = "classification",
    READ = "read",
    GENERATION = "generation"
}

export interface ApiReportParam {
    name: string
    type: "boolean" | "string" | "enum"
    data: ApiReportParamData
}

export interface ApiReportParamData {
    variants?: string[]
    value: boolean | string
}

interface CreateRequest {
    title: string
    source_image: string
}

interface UpdateRequest {
    title: string
    params: ApiReportParam[]
}

export class ReportApi {
    static async create(title: string, sourceImage: string): Promise<ApiReportModel> {
        return makeHttpRequest<CreateRequest, ApiReportModel>(HttpMethod.POST,
            reportApiPath(`/api/v1/report`),
            {
                title,
                source_image: sourceImage
            },
            {
                accessToken: getAccessToken()
            })
    }

    static async get(id: number): Promise<ApiReportModel> {
        return makeHttpRequest<void, ApiReportModel>(HttpMethod.GET, reportApiPath(`/api/v1/report/${id}`), null, {
            accessToken: getAccessToken()
        })
    }

    static getImageUrl(id: number, imageType: string): string {
        return reportApiPath(`/api/v1/report/${id}/image/${imageType}?auth_token=${getAccessToken()}`)
    }

    static async list(): Promise<ApiReportModel[]> {
        return makeHttpRequest<void, ApiReportModel[]>(HttpMethod.GET, reportApiPath("/api/v1/report"), null, {
            accessToken: getAccessToken()
        })
    }

    static async update(id: number, title: string, params: ApiReportParam[]): Promise<void> {
        return makeHttpRequest<UpdateRequest, void>(HttpMethod.PUT, reportApiPath(`/api/v1/report/${id}`), {
            title,
            params,
        }, {
            accessToken: getAccessToken()
        })
    }

    static async delete(id: number): Promise<void> {
        return makeHttpRequest(HttpMethod.DELETE, reportApiPath(`/api/v1/report/${id}`), null, {
            accessToken: getAccessToken()
        })
    }

    static async rephrase(id: number): Promise<ApiReportModel> {
        return makeHttpRequest<void, ApiReportModel>(HttpMethod.POST, reportApiPath(`/api/v1/report/${id}/rephrase`), null, {
            accessToken: getAccessToken()
        })
    }


    static async update_active(id: number, version: number): Promise<ApiReportModel> {
        return makeHttpRequest<void, ApiReportModel>(HttpMethod.POST, reportApiPath(`/api/v1/report/${id}/active/${version}`), null, {
            accessToken: getAccessToken()
        })
    }

    static async create_pdf(reportId: number): Promise<Blob> {
        const url = reportApiPath(`/api/v1/report/${reportId}/pdf?auth_token=${getAccessToken()}`);
        const response = await fetch(url, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`Ошибка при создании PDF: ${response.status} ${response.statusText}`);
        }

        return await response.blob();
    }

    // static create_pdf(id: number): string {
    //     return reportApiPath(`/api/v1/report/${id}/pdf?auth_token=${getAccessToken()}`)
    // }

}

function reportApiPath(path: string): string {
    return `${process.env.REPORT_API_URL}${path}`
}