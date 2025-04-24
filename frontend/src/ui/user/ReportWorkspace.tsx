import React, {ComponentPropsWithoutRef, ReactElement, useEffect, useMemo, useState} from "react";
import {useDispatch} from "react-redux";

import {classes, readableDateFromTimestamp} from "src/util";
import {AppDispatch} from "src/redux/store";
import {Report, ReportActions, ReportController, ReportImageType, ReportParam, ReportStatus} from "src/redux/report";

import {BlueButton, Center, Horizontal, Vertical, WhiteButton} from "src/ui/AppBase";
import {EnumTranslate, ParamGroupList, ParamGroupTranslate, ParamTranslate} from "src/ui/view";
import {ReportParamGroup} from "src/ui/user/ReportParamGroup";

import Styles from "./ReportWorkspace.module.scss"
import {retry} from "@reduxjs/toolkit/query";
import {scryRenderedComponentsWithType} from "react-dom/test-utils";

interface ReportWorkspaceProps {
    report: Report
}

const REPORT_REFRESH_TIMEOUT = 2500

export function ReportWorkspace({report}: ReportWorkspaceProps) {
    let [imageTypes, setImageTypes] = useState([])
    let [fullscreen, setFullscreen] = useState(false)
    let dispatch = useDispatch<AppDispatch>()

    let paramMap = useMemo(() => reportParamMap(report.params), [report.params])

    const [canNavigateForward, setCanNavigateForward] = useState(false);
    const [canNavigateBack, setCanNavigateBack] = useState(false);

    // Loading params
    useEffect(() => {
        if (report.params == null || report.texts == null) {
            dispatch(ReportController.get(report.id))
        }
        else {
            let currReportIdx: number = report.texts.findIndex(text => text.active)
            let reportsAmount: number = report.texts.length

            setCanNavigateForward((reportsAmount>1) && (currReportIdx < reportsAmount));
            setCanNavigateBack((reportsAmount>1) && (currReportIdx>0));
        }
    }, [report]);

    // Refreshing report
    useEffect(() => {
        let needClassification = Object
        .values(report.statuses)
        .filter(status => status !== ReportStatus.CLASSIFICATION && status !== ReportStatus.GENERATION)
        .length;

        if (needClassification == 0) {
            return
        }

        let interval = setInterval(() => dispatch(ReportController.get(report.id)), REPORT_REFRESH_TIMEOUT)

        return function () {
            clearInterval(interval)
        }
    }, [report]);

    function chooseImage(imageType: ReportImageType) {
        // Remove type if already presented
        if (imageTypes.includes(imageType)) {
            setImageTypes(imageTypes => imageTypes.filter(tt => tt != imageType))
            return
        }

        setImageTypes(imageTypes => imageTypes.concat([imageType]))
    }

    // function updateReport() {
    //     dispatch(ReportController.update(report))
    // }

    function handleSave() {
        dispatch(ReportController.update(report))
        .then(() => {
            dispatch(ReportController.get(report.id));
        });
    }

    function deleteReport() {
        dispatch(ReportController.delete(report.id))
    }
    
    function rephraseReport() {
        dispatch(ReportController.rephrase(report.id))
        .then(() => {
            dispatch(ReportController.get(report.id));
        })
    }

    function createPDF() {
        dispatch(ReportController.create_pdf(report.id))
    }

    function closeReport() {
        dispatch(ReportActions.resetCurrent())
    }

    function renderMaskButtons() {
        let imageTypeMap = {
            OD: ReportImageType.OD_CONTOUR,
            MAC: ReportImageType.MAC_CONTOUR,
            AV: ReportImageType.AV_SEGMENTATION,
        }

        let buttons = Object
            .keys(imageTypeMap)
            .filter(service => {
                return report.statuses[service] == ReportStatus.LOCALIZATION ||
                    report.statuses[service] == ReportStatus.CLASSIFICATION
            })
            .map((service, index) => {
                return (
                    imageTypes.includes(imageTypeMap[service]) ?
                        <BlueButton key={index}
                                    icon="check"
                                    onClick={() => chooseImage(imageTypeMap[service])}>
                            {ParamGroupTranslate[service]}
                        </BlueButton> :
                        <WhiteButton key={index}
                                     onClick={() => chooseImage(imageTypeMap[service])}>
                            {ParamGroupTranslate[service]}
                        </WhiteButton>
                )
            })

        if (buttons.length < Object.keys(imageTypeMap).length) {
            buttons.push(
                <Center key={buttons.length} className={Styles.LoadingButtons}>Ожидание локализации</Center>
            )
        }

        return (
            <Vertical gap="10px">
                {buttons}
            </Vertical>
        )
    }

    function getActiveText() {
        let activeText = report.texts.find(text => text.active === true);

        let getEnum = (name: string): string => {
            return `${EnumTranslate[paramMap[name].data.value as string].toLowerCase()}`
        }

        let getString = (name: string): string => {
            return `${(paramMap[name].data.value as string).toLowerCase()}`
        }

        if (activeText) {
            return activeText.text
        }
        else {
            return (
                `ДЗН: ${getEnum("od_color")}, размер ${getEnum("od_size")}, ${getEnum("od_shape")} формa, границы ${getEnum("od_border")}, экскавация ${getEnum("od_excavation_size")} размера, расположение ${getEnum("od_excavation_location")}, э/д = ${getString("od_excavation_ratio")}, сосудистый пучок ${getEnum("od_vessels_location")}\n\n` +
                `Артерии: калибр ${getEnum("vessels_art_caliber")}, ход ${getEnum("vessels_art_course")}, извитость ${getEnum("vessels_art_turtuosity")}, бифуркация ${getEnum("vessels_art_bifurcation")}\n\n` +
                `Вены: калибр ${getEnum("vessels_vein_caliber")}, ход ${getEnum("vessels_vein_course")}, извитость ${getEnum("vessels_vein_turtuosity")}, бифуркация ${getEnum("vessels_vein_bifurcation")}\n\n` +
                `Макула: макулярный рефлекс ${getEnum("macula_macular_reflex")}, фовеолярный рефлекс ${getEnum("macula_foveal_reflex")}`
            ) 
        }
    }

    function renderReportText() {
        switch (report.status) {
            case ReportStatus.CLASSIFICATION:
            case ReportStatus.READ:
                if (paramMap == null) {
                    return <Center className={Styles.LoadingReportText}>Загрузка</Center>
                }
           
                return <Center className={Styles.LoadingReportText}>Классифицировано, ожидание генерация</Center>;
                
            case ReportStatus.GENERATION:
                if (!report.texts) { // TODO Странно, почему текст не загружается сразу? 
                    return <Center className={Styles.LoadingReportText}>Загрузка...</Center>;
                }
                
                let activeText = getActiveText()

                // if (activeText) {
                //     return <div>{activeText.text}</div>;
                // }
                
                // return <div>Ошибка, активный текст не найден</div>;
                return activeText

            case ReportStatus.UPDATING:
                return <Center className={Styles.LoadingReportText}>Применение изменений</Center>;

            default:
                return <Center className={Styles.LoadingReportText}>Ожидание классификации</Center>
        }
    }

    function renderReportCopyButton() {
        switch (report.status) {
            case ReportStatus.GENERATION:
            case ReportStatus.READ:
                return (
                    <WhiteButton 
                        icon="content_paste" 
                        onClick={async () => {
                            await navigator.clipboard.writeText(getReportText());
                        }}
                        className={Styles.CopyButton} // Добавлен класс
                    >
                        Копировать отчет
                    </WhiteButton>
                );
    
            default:
                return <></>;
        }
    }

    function renderReportRephraseButton() {
        switch (report.status) {
            case ReportStatus.GENERATION:
            case ReportStatus.READ:
                return (
                    <WhiteButton 
                        icon="autorenew" 
                        onClick={rephraseReport}
                        className={Styles.RephraseButton}
                    >
                        Детализировать
                    </WhiteButton>
                );
    
            default:
                return <></>;
        }
    }

    function renderReportPDFButton() {
        switch (report.status) {
            case ReportStatus.GENERATION:
            case ReportStatus.READ:
                return (
                    <WhiteButton 
                        icon="picture_as_pdf" 
                        onClick={createPDF}
                        className={Styles.PDFButton} // Добавлен класс
                    >
                        Скачать PDF
                    </WhiteButton>
                );
    
            default:
                return <></>;
        }
    }


    function navigateForward() {
        let activeText = report.texts.find(text => text.active === true);

        dispatch(ReportController.update_active(report.id, activeText.version + 1))
        .then(() => {
            dispatch(ReportController.get(report.id));
        })

    }

    function navigateBack() {
        let activeText = report.texts.find(text => text.active === true);

        dispatch(ReportController.update_active(report.id, activeText.version - 1))
        .then(() => {
            dispatch(ReportController.get(report.id));
        })
    }

    // TODO Это точно надо переименовать
    function getNavigationNumbers() {
        if (!report.texts) { // TODO Странно, почему текст не загружается сразу? 
            return `Загрузка...`
        }

        const index = report.texts.findIndex(text => text.active);
    
        if (index !== -1) {
            return `${index + 1} / ${report.texts.length}`;
        }

        return null;
    }

    function renderVersionNavigation() {
        switch (report.status) {
            case ReportStatus.GENERATION:
            case ReportStatus.READ:
                return (
                    <Horizontal className={Styles.VersionNavigation} gap="10px">
                        <WhiteButton
                            icon="chevron_left"
                            onClick={navigateBack}
                            disabled={!canNavigateBack}
                            className={Styles.NavigateButton}
                            aria-label="Предыдущая версия" // Accessibility
                        />
                        <div>{getNavigationNumbers()}</div>
                        <WhiteButton
                            icon="chevron_right"
                            onClick={navigateForward}
                            disabled={!canNavigateForward}
                            className={Styles.NavigateButton}
                            aria-label="Следующая версия" // Accessibility
                        />
                    </Horizontal>
                );
            default:
                return <></>;
        }
        
        
    }
    
    function getReportText(): string {
            if (!report.texts) {
                return ""
            }
            return getActiveText()
    }

    function renderParams() {
        if (report.params) {
            return ParamGroupList
                .map((paramGroup, index) =>
                    <ReportParamGroup key={index} report={report} paramGroup={paramGroup}/>)
        }

        return <Center className={Styles.LoadingParams}>Загрузка параметров</Center>
    }

    function renderSaveButton() {
        switch (report.status) {
            case ReportStatus.GENERATION:
            case ReportStatus.READ:
                return (
                    <BlueButton onClick={handleSave}>
                        Сохранить
                    </BlueButton>
                )

            default:
                return (
                    <BlueButton disabled>
                        Сохранить
                    </BlueButton>
                )
        }
    }

    function renderTextWarning() {
        switch (report.status) {
            case ReportStatus.GENERATION:
                if (!report.texts) { // TODO Странно, почему текст не загружается сразу? 
                    return
                }

                let activeText = report.texts.find(text => text.active === true);

                if (!activeText) {
                    return <svg
                    className={Styles.WarningIcon}
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    width="24px"
                    height="24px">
                    <path
                    fill="currentColor"
                    d="
                        M12 2 L1 22 H23 L12 2 Z
                        M13 17 H11 V15 H13 V17 Z
                        M13 13 H11 V7  H13 V13 Z
                    "
                    />
                </svg>
                }
                return 
            default:
                return <Center className={Styles.LoadingReportText}></Center>
        }
    }

    return (
        <Horizontal grow="2">
            <Vertical gap="40px" className={Styles.Center}>
                <Horizontal center>
                    <Vertical gap="5px" grow="2">
                        <div className={Styles.Title}>{report.title}</div>
                        <div className={Styles.TimeHint}>{readableDateFromTimestamp(report.createdAt)}</div>
                    </Vertical>
                    <WhiteButton icon="close" onClick={closeReport}>
                        Закрыть
                    </WhiteButton>
                </Horizontal>

                <Vertical gap="20px">
                    <div className={Styles.Title}>Изображение</div>
                    <Horizontal gap="30px" className={Styles.Section}>
                        <div className={fullscreen ? Styles.ImageWrapFullscreen : Styles.ImageWrap}
                             onClick={() => setFullscreen(!fullscreen)}>
                            <img alt=""
                                 src={ReportController.getImageUrl(report.id, ReportImageType.SOURCE)}
                                 className={classes(fullscreen ? Styles.ImageFullScreen : Styles.Image, Styles.SourceImage)}/>

                            {
                                imageTypes.map((imageType, index) =>
                                    <img key={index}
                                         alt=""
                                         src={ReportController.getImageUrl(report.id, imageType)}
                                         className={classes(fullscreen ? Styles.ImageFullScreen : Styles.Image, Styles.MaskImage)}/>
                                )
                            }
                        </div>

                        <Vertical gap="20px" grow="2">
                            <Vertical gap="10px">
                                <div className={Styles.SubTitle}>Выделить зону</div>
                                <div className={Styles.Hint}>Можно использовать несколько масок</div>
                            </Vertical>

                            {renderMaskButtons()}
                        </Vertical>
                    </Horizontal>
                </Vertical>

                <Vertical gap="20px">
                    <div className={Styles.TitleContainer}>
                        <div className={Styles.Title}>Отчет</div>
                        {/* <div> <span style={{color: 'orange', marginLeft: '10px'}}>⚠</span> </div> */}
                        {/* <svg
                            className={Styles.WarningIcon}
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            width="24px"
                            height="24px"
                        >
                            <path
                            fill="currentColor"
                            d="
                                M12 2 L1 22 H23 L12 2 Z
                                M13 17 H11 V15 H13 V17 Z
                                M13 13 H11 V7  H13 V13 Z
                            "
                            />
                        </svg> */}
                        {renderTextWarning()}
                    </div>

                    <div className={Styles.Section}>
                        {renderReportText()}
                    </div>
                    {renderVersionNavigation()}
                </Vertical>

                <Horizontal gap="10px">
                    {renderReportCopyButton()}
                    {renderReportRephraseButton()}
                    {renderReportPDFButton()}
                    <WhiteButton icon="close"
                                 className={Styles.DeleteButton}
                                 onClick={deleteReport}>
                        Удалить
                    </WhiteButton>
                </Horizontal>
            </Vertical>

            <Vertical className={Styles.Right} grow="2">
                <Vertical gap="15px" className={Styles.Header}>
                    <div className={Styles.Title}>Результат</div>
                    <div className={Styles.Hint}>
                        Текст финального отчета строится на основе параметров
                    </div>
                </Vertical>
                <Vertical grow="2" className={Styles.Params}>
                    {renderParams()}
                </Vertical>
                <Vertical className={Styles.Footer}>
                    {renderSaveButton()}
                </Vertical>
            </Vertical>
        </Horizontal>
    )
}

interface ReportTextTitleProps extends ComponentPropsWithoutRef<"span"> {
}

function ReportTextTitle({children}: ReportTextTitleProps): ReactElement {
    return <span className={Styles.ReportTextTitle}>{children}</span>
}

function reportParamMap(params: ReportParam[]): { [key: string]: ReportParam } {
    return params?.reduce((map, param) => {
        map[param.name] = param
        return map
    }, {})
}
