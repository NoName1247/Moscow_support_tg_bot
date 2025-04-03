CREATE TABLE IF NOT EXISTS public.requests
(
    id bigint NOT NULL DEFAULT nextval('"Requests_id_seq"'::regclass),
    user_name text COLLATE pg_catalog."default",
    user_link text COLLATE pg_catalog."default" NOT NULL,
    user_id text COLLATE pg_catalog."default" NOT NULL,
    user_status text COLLATE pg_catalog."default",
    competition text COLLATE pg_catalog."default",
    date daterange NOT NULL,
    request text COLLATE pg_catalog."default",
    status smallint NOT NULL,
    support_id bigint NOT NULL,
    CONSTRAINT "Requests_pkey" PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.supports
(
    id bigint NOT NULL DEFAULT nextval('supports_id_seq'::regclass),
    username text COLLATE pg_catalog."default",
    user_id bigint NOT NULL,
    karma bigint NOT NULL,
    CONSTRAINT supports_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.supports
    OWNER to postgres;