import DefaultIdea from "./DefaultIdea";

const defaultIdeas = [
  {
    idea: "C'est Quoi SolarNasih",
    moreContext: "Explique-moi ce qu'est SolarNasih, ses fonctionnalités principales et comment il peut aider dans le domaine de l'énergie solaire au Maroc",
  },
  {
    idea: "Qui a développé SolarNasih",
    moreContext:
      "Parle-moi de l'équipe qui a développé SolarNasih, les technologies utilisées et l'architecture du système",
  },
  { 
    idea: "Les Nouvelles Alert", 
    moreContext: "Donne-moi les dernières nouvelles et actualités sur l'énergie solaire au Maroc, les nouvelles réglementations et les projets en cours" 
  },
  {
    idea: "Comment utiliser SolarNasih",
    moreContext: "Explique-moi comment utiliser SolarNasih efficacement, les différentes fonctionnalités disponibles et des exemples d'utilisation pratiques",
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
