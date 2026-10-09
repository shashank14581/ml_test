import { useEffect, useState } from 'react';
import exam from '../questions.json';

type Draft = { choices: Record<number, number>; responses: Record<number, string>; failed: boolean; submittedAt: string | null };
const KEY = 'ml-thinking-exam-v1';
const blank: Draft = { choices: {}, responses: {}, failed: false, submittedAt: null };
const initial = (): Draft => { try { const saved = localStorage.getItem(KEY); return saved ? { ...blank, ...JSON.parse(saved) } : blank; } catch { return blank; } };
const questions = exam.questions;
const getScore = (choices: Record<number,number>) => questions.reduce((s,q,i) => s + (choices[i] === q.answer ? 2 : 0), 0);

export default function App() {
  const [draft, setDraft] = useState<Draft>(initial);
  const [index, setIndex] = useState(0);
  const [confirming, setConfirming] = useState(false);
  const [started, setStarted] = useState(false);
  useEffect(() => { localStorage.setItem(KEY, JSON.stringify(draft)); }, [draft]);
  useEffect(() => {
    if (!started || draft.submittedAt || draft.failed) return;
    const detect = () => { if (document.hidden) setDraft(d => ({...d, failed:true})); };
    document.addEventListener('visibilitychange',detect);
    return () => document.removeEventListener('visibilitychange',detect);
  }, [started,draft.submittedAt,draft.failed]);
  const q = questions[index];
  const finished = !!draft.submittedAt;
  const completed = questions.filter((_,i) => draft.choices[i] !== undefined && !!draft.responses[i]?.trim()).length;
  const objective = getScore(draft.choices);
  const downloadable = () => {
    const payload = { candidate:exam.candidate, version: exam.version, submittedAt:draft.submittedAt, integrityStatus:draft.failed?'FLAGGED':'No tab switch recorded in this browser session', objectiveScore:objective, objectiveTotal:40, writtenScore:'Awaiting manual review (up to 60)', responses:questions.map((x,i)=>({number:i+1, title:x.title, domain:x.domain, selectedOption: draft.choices[i] === undefined ? null : x.options[draft.choices[i]], correctOption:x.options[x.answer], reasoning:draft.responses[i] || '', reviewerRubric:x.rubric})) };
    const url=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));
    const a=document.createElement('a'); a.href=url;a.download='ml_exam_geetanjali_submission.json';a.click();URL.revokeObjectURL(url);
  };
  const updateChoice=(n:number)=>setDraft(d=>({...d,choices:{...d.choices,[index]:n}}));
  const updateResponse=(v:string)=>setDraft(d=>({...d,responses:{...d.responses,[index]:v}}));
  return <main className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
    <div className="mx-auto max-w-6xl">
      <header className="mb-6 rounded-2xl bg-slate-900 border border-slate-800 p-6">
        <div className="text-xs tracking-widest uppercase text-cyan-400 font-bold">Trainee evaluation • Applied ML</div>
        <h1 className="text-3xl md:text-4xl font-bold mt-2">{exam.title}</h1>
        <p className="text-slate-400 mt-3">Candidate: <strong className="text-white">{exam.candidate}</strong> · 20 applied ML scenarios · 100 points total</p>
        <p className="text-slate-400 mt-2">Make a decision, then demonstrate how you would implement it. Give explicit features, labels, splits, pseudocode/SQL, metrics, assumptions and failure modes where relevant.</p>
        <div className="mt-4 grid sm:grid-cols-3 gap-2 text-sm"><div className="rounded-lg bg-slate-800 p-3">40 pts · 20 decisions, automatically graded</div><div className="rounded-lg bg-slate-800 p-3">60 pts · reasoning and implementation, manually reviewed</div><div className="rounded-lg bg-slate-800 p-3">Progress: {completed}/20 fully completed</div></div>
      </header>
      {draft.failed && !finished && <div role="alert" className="rounded-xl border border-red-500 bg-red-950 p-5 mb-5"><h2 className="text-xl font-bold">Assessment flagged: tab/window switch detected</h2><p className="mt-1">This browser-based check is a deterrent, not secure proctoring. Your draft is kept locally. Submit/export only for administrative review.</p></div>}
      {!started && !finished ? <section className="rounded-xl bg-slate-900 border border-slate-700 p-6">
        <h2 className="text-xl font-semibold">Assessment instructions</h2>
        <p className="mt-2 text-slate-300">Each question has a scenario, a decision worth 2 points and written reasoning worth 3 points. Reasoning is evaluated by a human using a three-part rubric. Do not just name an algorithm: define deployment decisions, measurable success and implementation steps.</p>
        <p className="mt-3 text-amber-300">Once started, switching tabs or minimizing this page flags the attempt. This does not provide secure identity or exam enforcement. Answers are saved only to this browser until you export them.</p>
        <button className="bg-cyan-400 text-slate-950 font-bold rounded-lg px-6 py-3 mt-5" onClick={()=>setStarted(true)}>Start / resume assessment</button>
      </section> : !finished ? <>
        <div className="flex gap-2 flex-wrap mb-4">{questions.map((_,i)=><button key={i} aria-label={`Go to question ${i+1}`} onClick={()=>setIndex(i)} className={`rounded-md w-10 h-10 border ${i===index?'bg-cyan-400 text-slate-950 border-cyan-400':draft.choices[i]!==undefined&&draft.responses[i]?.trim()?'bg-emerald-950 border-emerald-700':'bg-slate-900 border-slate-700'}`}>{i+1}</button>)}</div>
        <article className="rounded-2xl bg-slate-900 border border-slate-800 p-5 md:p-8">
          <div className="text-sm font-semibold text-cyan-400 uppercase tracking-wider">Case {index+1} / 20 • {q.domain}</div>
          <h2 className="mt-2 text-2xl font-bold">{q.title}</h2>
          <p className="mt-4 leading-relaxed text-slate-200">{q.scenario}</p>
          <div className="my-5 rounded-xl border-l-4 border-cyan-400 bg-slate-800 p-4"><strong>Your implementation challenge</strong><p className="mt-1">{q.task}</p></div>
          <fieldset className="space-y-3"><legend className="font-semibold mb-3">Part A — Select the best immediate decision (2 pts)</legend>{q.options.map((o,j)=><label key={j} className={`flex gap-3 cursor-pointer rounded-lg border p-3 ${draft.choices[index]===j?'border-cyan-400 bg-slate-800':'border-slate-700'}`}><input type="radio" className="accent-cyan-400" name={'q'+index} checked={draft.choices[index]===j} onChange={()=>updateChoice(j)}/><span>{String.fromCharCode(65+j)}. {o}</span></label>)}</fieldset>
          <label htmlFor="reasoning" className="block mt-7 font-semibold">Part B — Explain your design and implementation (3 pts)</label>
          <p className="text-sm text-slate-400 mt-1 mb-2">Show your logic, not just buzzwords. Pseudocode, metrics, validation and potential failures are encouraged.</p>
          <textarea id="reasoning" rows={10} value={draft.responses[index]||''} onChange={e=>updateResponse(e.target.value)} placeholder="I would define the target as...&#10;Pseudocode / SQL...&#10;My evaluation would be...&#10;Failure modes and safeguards..." className="w-full rounded-lg bg-slate-950 border border-slate-600 p-4 focus:outline-none focus:border-cyan-400"/>
          <div className="mt-5 flex flex-wrap justify-between gap-3"><button className="border border-slate-600 rounded-lg px-5 py-2 disabled:opacity-40" disabled={index===0} onClick={()=>setIndex(i=>i-1)}>Previous</button>{index<19?<button className="bg-cyan-400 text-slate-950 font-bold rounded-lg px-6 py-2" onClick={()=>setIndex(i=>i+1)}>Next case →</button>:<button className="bg-emerald-500 text-slate-950 font-bold rounded-lg px-6 py-2" onClick={()=>setConfirming(true)}>Review & submit</button>}</div>
        </article>
        {confirming && <section className="mt-5 p-5 rounded-xl bg-slate-900 border border-amber-500"><h2 className="font-bold text-lg">Submit this attempt?</h2><p className="mt-2">{completed}/20 fully completed. Incomplete responses receive zero for unanswered objective items; written responses require manual marking. Submitting reveals the answer guidance and locks this attempt in this browser.</p><div className="flex gap-3 mt-4"><button className="bg-emerald-500 text-slate-950 rounded-lg px-5 py-2 font-bold" onClick={()=>{setDraft(d=>({...d,submittedAt:new Date().toISOString()}));setConfirming(false)}}>Submit and reveal feedback</button><button className="border border-slate-500 rounded-lg px-5 py-2" onClick={()=>setConfirming(false)}>Continue working</button></div></section>}
      </> : <section className="space-y-5">
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl"><h2 className="text-2xl font-bold">Submitted • Objective score: {objective}/40</h2><p className="mt-2">Written implementation and reasoning: awaiting human marking (maximum 60 points). An objective score is not the final assessment score.</p><p className="mt-2 text-amber-300">{draft.failed ? 'Tab-switch flag recorded: needs supervisor review.' : 'No tab-switch flag saved; this is not verified proctoring.'}</p><button className="bg-cyan-400 text-slate-950 rounded-lg font-bold px-5 py-3 mt-4" onClick={downloadable}>Export submission + review rubric (JSON)</button><p className="text-sm text-slate-400 mt-3">Export the result before clearing browser data. Results are not uploaded or emailed automatically.</p></div>
        {questions.map((x,i)=><details key={i} className="border border-slate-700 bg-slate-900 rounded-xl p-5"><summary className="cursor-pointer font-semibold">#{i+1} {x.title} · {draft.choices[i]===x.answer?'2/2 objective pts':'0/2 objective pts'} · written pending</summary><p className="mt-3"><strong>Correct decision:</strong> {x.options[x.answer]}</p><p className="mt-2"><strong>Why:</strong> {x.explanation}</p><p className="mt-2"><strong>Submitted reasoning:</strong> {draft.responses[i]?.trim() || '(blank)'}</p><p className="mt-3 font-bold">Human reviewer checklist (1 point each)</p><ol className="list-decimal ml-5 mt-2 space-y-1">{x.rubric.map((r,j)=><li key={j}>{r}</li>)}</ol></details>)}
      </section>}
    </div>
  </main>;
}
