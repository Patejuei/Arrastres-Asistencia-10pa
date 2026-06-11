-- Script de migración para agregar el campo 'esquina' a la tabla 'actos_servicio'
-- Ejecutar este script en el editor SQL de Supabase

ALTER TABLE public.actos_servicio ADD COLUMN esquina TEXT NULL;
