import { useState } from "react";

export default function CampoSenha({
  id,
  name,
  label,
  dica,
  value,
  onChange,
  autoComplete,
  minLength,
  maxLength,
  invalido = false,
  descricaoId,
}) {
  const [visivel, setVisivel] = useState(false);

  return (
    <div className="campo">
      <label className="campo-rodape" htmlFor={id}>
        {label}
        {dica ? <span className="campo-dica">{dica}</span> : null}
      </label>
      <div className="campo-senha">
        <input
          id={id}
          type={visivel ? "text" : "password"}
          name={name}
          value={value}
          onChange={(evento) => onChange(evento.target.value)}
          autoComplete={autoComplete}
          minLength={minLength}
          maxLength={maxLength}
          aria-invalid={invalido}
          aria-describedby={invalido ? descricaoId : undefined}
          required
        />
        <button
          className="botao-olho"
          type="button"
          aria-label={visivel ? "Ocultar senha" : "Mostrar senha"}
          aria-pressed={visivel}
          onClick={() => setVisivel(!visivel)}
        >
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            {visivel ? (
              <>
                <path d="M3 3l18 18" />
                <path d="M10.6 10.6a2 2 0 002.8 2.8" />
                <path d="M9.9 5.2A10.8 10.8 0 0112 5c5 0 8.5 4.5 9.5 7-.4 1-1.3 2.3-2.6 3.5" />
                <path d="M6.2 6.2C3.9 7.6 2.7 9.8 2.5 12c.5 1.2 2.7 5 7.5 6.6a10 10 0 004 .3" />
              </>
            ) : (
              <>
                <path d="M2.5 12S6 5 12 5s9.5 7 9.5 7-3.5 7-9.5 7-9.5-7-9.5-7z" />
                <circle cx="12" cy="12" r="2.5" />
              </>
            )}
          </svg>
        </button>
      </div>
    </div>
  );
}