CREATE TABLE IF NOT EXISTS public.requests
(
    id bigserial NOT NULL,
    user_name text,
    user_link text NOT NULL,
    user_id text NOT NULL,
    user_status text,
    competition text,
    date daterange NOT NULL,
    request text,
    status smallint NOT NULL,
    support_id bigint NOT NULL,
    CONSTRAINT "Requests_pkey" PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.supports
(
    id bigint NOT NULL,
    username text,
    user_id bigint NOT NULL,
    karma bigint NOT NULL,
    CONSTRAINT supports_pkey PRIMARY KEY (id)
)

ALTER TABLE IF EXISTS public.supports
    OWNER to postgres;