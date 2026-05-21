'use client';

import { useGenerationContext } from '@/context/GenerationContext';

export function useGeneration() {
    return useGenerationContext();
}