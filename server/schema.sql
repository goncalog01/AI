drop table if exists slots;
drop type if exists slot_state;

create type slot_state as enum ('free', 'occupied', 'reserved', 'unknown');

create table slots
   (slot_id 	         smallint         not null unique,
    slot_camera_id       smallint         not null,
    slot_latitude        double precision not null,
    slot_longitude       double precision not null,
    slot_state           slot_state       not null,
    reserved_until       time,
    last_updated         time,
    constraint pk_slot primary key(slot_id));

alter table slots
add constraint reserved_time_not_null check (slot_state <> 'reserved' or reserved_until is not null);

alter table slots
add constraint last_updated_not_null check (slot_state <> 'unknown' or last_updated is null);
