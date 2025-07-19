import DefaultIdea from "./DefaultIdea";

const defaultIdeas = [
  {
    idea: "C'eat Quoi SolarNasih",
    moreContext: "Donner moi des idées de contenu pour SolarNasih",
  },
  {
    idea: "Qui a developpé SolarNasih",
    moreContext:
      "Donner moi l'equipe qui a developpé SolarNasih et les technologies utilisées",
  },
  { idea: "les Nouvelles Alert", moreContext: "Donner moi les dernières nouvelles Sur l'energier Solaire Au maroc" },
  {
    idea: "Comment utiliser SolarNasih",
    moreContext: "Donner moi des idées de contenu pour utiliser SolarNasih",
  },
];

export default function DefaultIdeas({ visible = true }) {
  return (
    <div className={`row1 ${visible ? "block" : "hidden"}`}>
      <DefaultIdea ideas={defaultIdeas.slice(0, 2)} />
      <DefaultIdea
        ideas={defaultIdeas.slice(2, 4)}
        myclassNames="hidden md:visible"
      />
    </div>
  );
}
