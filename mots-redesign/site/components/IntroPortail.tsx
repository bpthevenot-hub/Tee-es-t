'use client'

import { useEffect, useRef, useState } from 'react'
import EcgLine from '@/components/EcgLine'
import { TEL_AFFICHE, TEL_HREF } from '@/lib/infos'

/**
 * Portail d'introduction plein écran, affiché AVANT d'entrer sur le site
 * (une fois par session de navigation). Ne remplace pas la page d'accueil :
 * il se superpose, puis s'efface.
 *
 * Vidéo : lit /videos/intro-medecins.mp4 si le fichier existe (fond sombre,
 * muet, en boucle). Sans fichier — ou si prefers-reduced-motion — bascule
 * sur une scène animée intégrée (dégradé marine + orbes + ECG).
 *
 * Accessibilité : rendu client uniquement (le HTML servi reste la page
 * d'accueil complète), focus posé sur le bouton d'entrée, Échap pour passer,
 * bouton « Passer l'introduction » toujours visible.
 */
const CLE_SESSION = 'mots-intro-vue'

export default function IntroPortail() {
  const [visible, setVisible] = useState(false)
  const [videoOk, setVideoOk] = useState(true)
  const [mouvementReduit, setMouvementReduit] = useState(false)
  const boutonEntrer = useRef<HTMLButtonElement>(null)
  const conteneur = useRef<HTMLDivElement>(null)

  useEffect(() => {
    try {
      if (sessionStorage.getItem(CLE_SESSION)) return
    } catch {
      /* stockage indisponible : on affiche quand même */
    }
    setMouvementReduit(window.matchMedia('(prefers-reduced-motion: reduce)').matches)
    setVisible(true)
  }, [])

  useEffect(() => {
    if (!visible) return
    boutonEntrer.current?.focus()
    document.body.style.overflow = 'hidden'
    const surTouche = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        fermer()
        return
      }
      // Focus-trap minimal : l'overlay est un dialog modal (aria-modal),
      // Tab doit boucler entre ses contrôles sans atteindre la page derrière.
      if (e.key !== 'Tab' || !conteneur.current) return
      const focusables = Array.from(
        conteneur.current.querySelectorAll<HTMLElement>('button, a[href]')
      )
      if (focusables.length === 0) return
      const premier = focusables[0]
      const dernier = focusables[focusables.length - 1]
      const actif = document.activeElement
      const dansOverlay = actif instanceof HTMLElement && conteneur.current.contains(actif)
      if (e.shiftKey && (!dansOverlay || actif === premier)) {
        e.preventDefault()
        dernier.focus()
      } else if (!e.shiftKey && (!dansOverlay || actif === dernier)) {
        e.preventDefault()
        premier.focus()
      }
    }
    window.addEventListener('keydown', surTouche)
    return () => {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', surTouche)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible])

  const fermer = () => {
    try {
      sessionStorage.setItem(CLE_SESSION, '1')
    } catch {
      /* sans stockage, l'intro reviendra — acceptable */
    }
    setVisible(false)
  }

  /**
   * Sous prefers-reduced-motion, la règle globale (globals.css) annule la
   * durée des animations mais PAS leur délai : avec `fill-mode: both`, le
   * texte resterait invisible pendant tout le délai. On n'anime donc pas.
   */
  const apparition = (delai: string) =>
    mouvementReduit ? undefined : { animation: `apparition 0.9s ease ${delai} both` }

  if (!visible) return null

  return (
    <div
      ref={conteneur}
      role="dialog"
      aria-modal="true"
      aria-label="Introduction — MOTS, prendre soin des soignants"
      className="fixed inset-0 z-[100] flex flex-col overflow-hidden bg-marine text-white"
    >
      {/* --- Fond : vidéo si disponible, sinon scène animée --- */}
      {videoOk && !mouvementReduit && (
        <video
          className="absolute inset-0 h-full w-full object-cover opacity-40"
          src="/videos/intro-medecins.mp4"
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          aria-hidden="true"
          onError={() => setVideoOk(false)}
        />
      )}
      <div aria-hidden="true" className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_120%,rgba(20,114,124,0.5),transparent_60%)]" />
      {(!videoOk || mouvementReduit) && (
        <>
          <div aria-hidden="true" className="orbe -top-24 left-1/4 h-96 w-96 bg-sapin-clair/35" />
          <div aria-hidden="true" className="orbe bottom-0 -right-20 h-80 w-80 bg-accent/20" style={{ animationDelay: '-7s' }} />
        </>
      )}
      <div aria-hidden="true" className="absolute inset-x-0 top-1/2 -translate-y-1/2">
        <EcgLine className="h-24 w-full text-ecume/25" />
      </div>

      {/* --- Passer --- */}
      <div className="relative flex justify-end p-4 sm:p-6">
        <button
          type="button"
          onClick={fermer}
          className="rounded-full border border-white/25 px-4 py-2 text-sm text-white/80 transition hover:bg-white/10 hover:text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
        >
          Passer l’introduction →
        </button>
      </div>

      {/* --- Message séquencé --- */}
      <div className="relative flex flex-1 flex-col items-center justify-center px-6 text-center">
        <p
          className="text-lg font-medium text-ecume/90 sm:text-xl"
          style={apparition('0.2s')}
        >
          Chaque jour, ils soignent des millions de Français.
        </p>
        <p
          className="titre-hero mt-5 max-w-3xl"
          style={apparition('1.1s')}
        >
          Mais qui prend soin
          <br />
          de nos soignants ?
        </p>
        <div style={apparition('2.1s')}>
          <p className="mx-auto mt-7 max-w-xl font-semibold text-white">
            Un médecin sur deux traverse un burnout au cours de sa carrière
            <span className="font-normal text-white/60"> — méta-analyse, 15 183 médecins français.</span>
          </p>
          <p className="mx-auto mt-3 max-w-xl text-white/80">
            Depuis 2010, les médecins de l’association MOTS écoutent et accompagnent,
            en toute confidentialité, les professionnels de santé qui traversent
            une période difficile.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-4">
            <button
              ref={boutonEntrer}
              type="button"
              onClick={fermer}
              className="inline-flex items-center gap-2.5 rounded-full bg-white px-8 py-4 text-lg font-semibold text-marine shadow-carte-haute transition hover:-translate-y-0.5 hover:bg-ecume focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
            >
              Entrer dans le site
            </button>
            <a href={TEL_HREF} className="bouton-appel !py-4">
              <span aria-hidden="true" className="point-vif h-2.5 w-2.5 rounded-full bg-white" />
              Besoin d’aide ? {TEL_AFFICHE}
            </a>
          </div>
          <p className="mt-5 text-sm text-white/55">Ligne d’écoute dédiée aux soignants — 7 j/7, confidentielle.</p>
        </div>
      </div>

      <div className="relative pb-6 text-center text-xs text-white/40">
        MOTS — Médecin · Organisation · Travail · Santé
      </div>
    </div>
  )
}
