--
-- PostgreSQL database dump
--

-- Dumped from database version 15.2 (Debian 15.2-1.pgdg110+1)
-- Dumped by pg_dump version 17.1 (Ubuntu 17.1-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

ALTER SCHEMA public OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: request; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.request (
    id character varying NOT NULL,
    service character varying NOT NULL,
    received timestamp without time zone DEFAULT now(),
    start_processing timestamp without time zone,
    end_processing timestamp without time zone,
    time_to_clean timestamp without time zone,
    exit_code smallint,
    std_out text,
    std_err text,
    CONSTRAINT request_check CHECK ((((end_processing IS NULL) = (exit_code IS NULL)) AND ((end_processing IS NULL) = (std_out IS NULL)) AND ((end_processing IS NULL) = (std_err IS NULL))))
);


ALTER TABLE public.request OWNER TO postgres;

--
-- Name: request_parameter; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.request_parameter (
    id integer NOT NULL,
    request_id character varying NOT NULL,
    name character varying(255) NOT NULL,
    value character varying DEFAULT ''::character varying NOT NULL
);


ALTER TABLE public.request_parameter OWNER TO postgres;

--
-- Name: COLUMN request_parameter.name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.request_parameter.name IS 'Tag name to pass to code. Never empty.';


--
-- Name: COLUMN request_parameter.value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.request_parameter.value IS 'Default to '''' for parameters with no values.';


--
-- Name: request_parameter_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.request_parameter_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.request_parameter_id_seq OWNER TO postgres;

--
-- Name: request_parameter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.request_parameter_id_seq OWNED BY public.request_parameter.id;


--
-- Name: request_parameter id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_parameter ALTER COLUMN id SET DEFAULT nextval('public.request_parameter_id_seq'::regclass);


--
-- Name: request_parameter request_parameter_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_parameter
    ADD CONSTRAINT request_parameter_pkey PRIMARY KEY (id);


--
-- Name: request_parameter request_parameter_request_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_parameter
    ADD CONSTRAINT request_parameter_request_name_key UNIQUE (request_id, name);


--
-- Name: request request_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request
    ADD CONSTRAINT request_pkey PRIMARY KEY (id);


--
-- Name: request_parameter request_parameter_request_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.request_parameter
    ADD CONSTRAINT request_parameter_request_fkey FOREIGN KEY (request_id) REFERENCES public.request(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: TABLE request; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.request TO ogc_api_user;


--
-- Name: TABLE request_parameter; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.request_parameter TO ogc_api_user;


--
-- Name: SEQUENCE request_parameter_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.request_parameter_id_seq TO ogc_api_user;


--
-- PostgreSQL database dump complete
--

