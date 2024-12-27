
export interface ICalendar {
    topics: string[];
    description: string;
}


export interface ICalendarDetail {
    topics: string[];
    description: string;
    host_id: number;
    google_calendar_id: string;
    created_at: string;
    updated_at: string;
}

export enum EnumEventKind {
    COFFEECHAT = "coffeechat",
    STUDYCAMP = "studycamp",
    TOYSTORY = "toystory",
    WRITING = "writing",
    CONFERENCE = "conference",
    SEMINAR = "seminar",
    MEETUP = "meetup",
    WORKSHOP = "workshop",
}

export interface IEventExtraSchema {
    og_image_url_intro?: string | null;
    og_image_url_list?: string | null;
    og_image_url_speakers?: string | null;
    og_image_url_participants?: string | null;
    og_image_url_contents?: string | null;
    og_image_url_questions?: string | null;
    og_image_url_sponsors?: string | null;
    og_image_url_staffs?: string | null;
}       