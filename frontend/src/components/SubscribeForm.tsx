import { useState, type FormEvent } from "react";
import { api, ApiError, isLive, type Channel, type Group, type Language } from "../api/client";
import type { Strings } from "../i18n/strings";

interface Props {
  wardId: string;
  lang: Language;
  t: Strings;
}

type Status = { state: "idle" } | { state: "sending" } | { state: "done" } | { state: "error"; message: string };

const GROUPS: Group[] = ["worker", "parent", "elderly"];

export default function SubscribeForm({ wardId, lang, t }: Props) {
  const [phone, setPhone] = useState("");
  const [group, setGroup] = useState<Group>("worker");
  const [language, setLanguage] = useState<Language>(lang);
  const [channel, setChannel] = useState<Channel>("whatsapp");
  const [status, setStatus] = useState<Status>({ state: "idle" });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setStatus({ state: "sending" });
    const digits = phone.replace(/\D/g, "").replace(/^91(?=\d{10}$)/, "");
    try {
      await api.subscribe({ phone: `+91${digits}`, wardId, group, language, channel });
      setStatus({ state: "done" });
    } catch (err) {
      setStatus({ state: "error", message: err instanceof ApiError ? err.message : t.loadFailed });
    }
  }

  if (!isLive()) return <p className="section-note">{t.subscribeOffline}</p>;

  if (status.state === "done") {
    return (
      <p className="subscribe-done" role="status">
        {t.subscribed}
      </p>
    );
  }

  return (
    <form className="subscribe" onSubmit={submit} aria-labelledby="sub-title">
      <h3 id="sub-title" className="section-title">
        {t.subscribeTitle}
      </h3>

      <label className="field">
        <span className="label">{t.phone}</span>
        <span className="phone-input">
          <span className="phone-prefix">+91</span>
          <input
            type="tel"
            inputMode="numeric"
            autoComplete="tel-national"
            required
            pattern="[0-9 ]{10,12}"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            aria-describedby="phone-hint"
          />
        </span>
        <span id="phone-hint" className="hint">
          {t.phoneHint}
        </span>
      </label>

      <fieldset className="field">
        <legend className="label">{t.whoFor}</legend>
        {GROUPS.map((g) => (
          <label key={g} className="choice">
            <input type="radio" name="group" checked={group === g} onChange={() => setGroup(g)} />
            {t.groups[g]}
          </label>
        ))}
      </fieldset>

      <div className="field-row">
        <fieldset className="field">
          <legend className="label">{t.alertLanguage}</legend>
          <label className="choice">
            <input type="radio" name="language" checked={language === "hi"} onChange={() => setLanguage("hi")} />
            <span lang="hi">हिन्दी</span>
          </label>
          <label className="choice">
            <input type="radio" name="language" checked={language === "en"} onChange={() => setLanguage("en")} />
            English
          </label>
        </fieldset>
        <fieldset className="field">
          <legend className="label">{t.channel}</legend>
          <label className="choice">
            <input type="radio" name="channel" checked={channel === "whatsapp"} onChange={() => setChannel("whatsapp")} />
            WhatsApp
          </label>
          <label className="choice">
            <input type="radio" name="channel" checked={channel === "sms"} onChange={() => setChannel("sms")} />
            SMS
          </label>
        </fieldset>
      </div>

      {status.state === "error" && (
        <p className="form-error" role="alert">
          {status.message}
        </p>
      )}
      <button type="submit" className="button-primary" disabled={status.state === "sending"}>
        {status.state === "sending" ? t.subscribing : t.subscribe}
      </button>
      <p className="hint">{t.subscribeNote}</p>
    </form>
  );
}
