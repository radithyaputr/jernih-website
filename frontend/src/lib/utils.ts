import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

export function formatTime(minutes: number): string {
  if (minutes >= 1440) return `${Math.round(minutes / 1440)} hari`
  if (minutes >= 60) return `${Math.round(minutes / 60)} jam`
  return `${minutes} menit`
}
