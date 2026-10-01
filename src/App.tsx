/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */
import { useRef, useEffect, useState } from 'react';
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import firebaseConfig from '../firebase-applet-config.json';

const app = initializeApp(firebaseConfig);
const db = getFirestore(app, firebaseConfig.firestoreDatabaseId);

const examQuestions = [
  { id: 1, q: "In Decision Trees, which impurity measure is more computationally expensive to compute than Entropy?", options: ["Gini Impurity", "Misclassification Error", "Variance Reduction", "Information Gain"], answer: "Gini Impurity" },
  { id: 2, q: "What is the primary effect of increasing 'min_samples_leaf' in a Decision Tree?", options: ["Increase model complexity", "Reduce overfitting", "Improve bias", "Decrease variance"], answer: "Reduce overfitting" },
  { id: 3, q: "How does XGBoost handle missing values by default?", options: ["Imputes with mean", "Throws an error", "Learns a default direction for split", "Drops rows"], answer: "Learns a default direction for split" },
  { id: 4, q: "Which parameter in XGBoost directly controls the complexity of the trees to prevent overfitting?", options: ["max_depth", "learning_rate", "gamma", "subsample"], answer: "gamma" },
  { id: 5, q: "What is the consequence of a very low 'learning_rate' in XGBoost?", options: ["Faster convergence", "Higher chance of overfitting", "Requires more trees (n_estimators) to converge", "Decreased model accuracy"], answer: "Requires more trees (n_estimators) to converge" },
  { id: 6, q: "Decision Tree pruning is used to:", options: ["Reduce training time", "Handle categorical features", "Reduce model complexity and prevent overfitting", "Increase tree depth"], answer: "Reduce model complexity and prevent overfitting" },
  { id: 7, q: "Which boosting algorithm is XGBoost primarily based on?", options: ["AdaBoost", "Gradient Boosting Machines", "Random Forest", "Bagging"], answer: "Gradient Boosting Machines" },
  { id: 8, q: "In XGBoost, what does the 'colsample_bytree' parameter do?", options: ["Samples rows", "Samples features per tree", "Samples features per split", "Controls tree depth"], answer: "Samples features per tree" },
  { id: 9, q: "Which of these is NOT a common technique to prevent overfitting in Decision Trees?", options: ["Pruning", "Setting max_depth", "Increasing min_samples_split", "Increasing tree depth"], answer: "Increasing tree depth" },
  { id: 10, q: "What objective function does XGBoost minimize?", options: ["Squared Error", "Regularized Loss Function", "Hinge Loss", "Cross-Entropy"], answer: "Regularized Loss Function" },
  { id: 11, q: "What is the purpose of the 'subsample' parameter in XGBoost?", options: ["Feature sub-sampling", "Row sub-sampling (stochastic gradient boosting)", "Learning rate reduction", "Regularization"], answer: "Row sub-sampling (stochastic gradient boosting)" },
  { id: 12, q: "Why are trees in XGBoost considered weak learners?", options: ["Because they have low predictive power alone", "Because they overfit easily", "Because they are deep", "Because they process data slowly"], answer: "Because they have low predictive power alone" },
  { id: 13, q: "What type of trees does XGBoost primarily use?", options: ["Regression trees", "Classification trees", "CART (Classification and Regression Trees)", "Random trees"], answer: "CART (Classification and Regression Trees)" },
  { id: 14, q: "What is the effect of 'reg_alpha' (L1 regularization) in XGBoost?", options: ["Prevents tree splitting", "Adds L1 penalty on leaf weights", "Adds L2 penalty on leaf weights", "Reduces number of trees"], answer: "Adds L1 penalty on leaf weights" },
  { id: 15, q: "How does XGBoost achieve its performance?", options: ["Parallel computation", "Block structure for data", "Cache-aware access", "All of the above"], answer: "All of the above" },
  { id: 16, q: "What happens if a Decision Tree is not pruned?", options: ["It generalizes better", "It is likely to overfit the training data", "It runs faster", "It becomes more interpretable"], answer: "It is likely to overfit the training data" },
  { id: 17, q: "In Gradient Boosting, what do the new trees predict?", options: ["The target values", "The residuals of the previous trees", "The absolute error", "The class labels"], answer: "The residuals of the previous trees" },
  { id: 18, q: "Which of these is true about XGBoost vs Random Forest?", options: ["XGBoost uses bagging, RF uses boosting", "XGBoost uses boosting, RF uses bagging", "Both use boosting", "Both use bagging"], answer: "XGBoost uses boosting, RF uses bagging" },
  { id: 19, q: "What is the role of 'tree_method' parameter in XGBoost?", options: ["Determines the algorithm to construct the tree", "Determines the boosting type", "Sets the learning rate", "Controls regularization"], answer: "Determines the algorithm to construct the tree" },
  { id: 20, q: "What does 'gamma' regularization in XGBoost act as?", options: ["A minimum loss reduction required to make a split", "A maximum loss allowed", "A penalty for leaf depth", "A learning rate scaler"], answer: "A minimum loss reduction required to make a split" }
];

export default function App() {
  const traineeName = "Geetanjali";
  const videoRef = useRef<HTMLVideoElement>(null);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [score, setScore] = useState<number | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing webcam:", err);
      }
    }
    setupCamera();

    const handleVisibilityChange = () => {
      if (document.hidden) {
        setFailed(true);
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);

  const handleSubmit = () => {
    let calculatedScore = 0;
    examQuestions.forEach(q => {
      if (answers[q.id] === q.answer) calculatedScore++;
    });
    setScore(calculatedScore);
  };

  if (failed) return <div className="text-red-600 text-3xl font-bold p-10">Exam Failed: Tab switching detected.</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">ML Proctored Exam</h1>
      <p>Trainee: {traineeName}</p>
      <div className="mt-4 border-2 border-red-500 p-4">
        <h2 className="font-bold text-red-600">Secure Webcam Monitoring</h2>
        <video ref={videoRef} autoPlay playsInline className="w-full h-48 mt-2 bg-black" />
      </div>
      <div className="mt-4">
        <h2 className="text-xl font-semibold mb-2">Test Content: Decision Trees and XGBoost</h2>
        {examQuestions.map((q) => (
          <div key={q.id} className="mb-6 p-4 border rounded shadow-sm">
            <p className="font-semibold mb-2">{q.id}. {q.q}</p>
            <div className="space-y-1">
              {q.options.map((option) => (
                <label key={option} className="flex items-center space-x-2">
                  <input type="radio" name={`question-${q.id}`} value={option} onChange={() => setAnswers({...answers, [q.id]: option})} />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
        <button onClick={handleSubmit} className="px-6 py-2 bg-green-600 text-white rounded font-bold">Submit Exam</button>
        {score !== null && <p className="mt-4 text-2xl">Final Score: {score} / {examQuestions.length}</p>}
      </div>
    </div>
  );
}
